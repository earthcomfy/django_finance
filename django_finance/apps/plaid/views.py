import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, ListView
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.item_remove_request import ItemRemoveRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_update import LinkTokenCreateRequestUpdate
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest
from plaid.model.sandbox_item_reset_login_request import SandboxItemResetLoginRequest

from django_finance.apps.plaid.models import Item, PlaidLinkEvent
from django_finance.apps.plaid.utils import plaid_config

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, ListView):
    """
    Plaid overview page showing all linked items.
    """

    model = Item
    context_object_name = "items"
    template_name = "plaid/index.html"

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(user=self.request.user)


class CreatePlaidLinkToken(LoginRequiredMixin, View):
    """
    Create a link_token and pass the temporary token to your app's client.
    https://plaid.com/docs/api/tokens/#linktokencreate
    """

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(self.request.body)
            plaid_id = data.get("plaid_id")
            new_accounts_detected = data.get("new_accounts_detected")

            link_request = LinkTokenCreateRequest(
                products=plaid_config.products,
                client_name=plaid_config.client_name,
                country_codes=plaid_config.country_codes,
                language=plaid_config.language,
                user=LinkTokenCreateRequestUser(client_user_id=str(self.request.user.id)),
                redirect_uri=plaid_config.redirect_uri,
                webhook=plaid_config.webhook_uri,
            )

            # In link update mode, include access token and an empty products array
            if plaid_id:
                link_request["access_token"] = Item.objects.filter(id=plaid_id).first().access_token
                link_request["products"] = []

            # Request new accounts in update mode
            if new_accounts_detected:
                link_request["update"] = LinkTokenCreateRequestUpdate(account_selection_enabled=True)

            link_response = plaid_config.client.link_token_create(link_request)
            return JsonResponse(link_response.to_dict(), status=201)
        except Exception as e:
            logger.error(
                f"Something went wrong in CreateLinkToken for user {self.request.user} -> {str(e)}",
            )
            return JsonResponse({}, status=500)


class ExchangePlaidPublicAccessToken(LoginRequiredMixin, View):
    """
    Exchange the public_token for a permanent access_token and item_id.
    https://plaid.com/docs/api/items/#itempublic_tokenexchange
    """

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(self.request.body)
            public_token = data.get("public_token")
            institution_id = data.get("institution_id")
            name = data.get("institution_name")

            items = Item.objects.filter(user=self.request.user)

            if items.filter(institution_id=institution_id).exists():
                messages.error(request, "You have already linked an item at this institution.")
                return render(request, "components/bank_cards.html", {"items": items})

            exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
            exchange_response = plaid_config.client.item_public_token_exchange(exchange_request)

            access_token = exchange_response.get("access_token")
            item_id = exchange_response.get("item_id")

            Item.objects.create(
                user=self.request.user,
                access_token=access_token,
                item_id=item_id,
                institution_id=institution_id,
                institution_name=name,
                status=Item.ItemStatusChoices.GOOD,
            )

            items = Item.objects.filter(user=self.request.user)
            return render(request, "components/bank_cards.html", {"items": items})
        except Exception as e:
            logger.error(f"Something went wrong in ExchangePublicAccessToken for user {self.request.user} -> {str(e)}")
            messages.error(request, "Something went wrong while integrating your bank account.")
            items = Item.objects.filter(user=self.request.user)
            return render(request, "components/bank_cards.html", {"items": items})


class PlaidRemoveItemView(LoginRequiredMixin, DeleteView):
    """
    Deletes a plaid item from Plaid and the database.
    """

    model = Item
    context_object_name = "item"
    template_name = "plaid/remove_item.html"
    success_url = reverse_lazy("dashboard")

    def delete(self, *args, **kwargs):
        self.object = self.get_object()

        try:
            access_token = self.object.access_token
            remove_request = ItemRemoveRequest(access_token=access_token)
            plaid_config.client.item_remove(remove_request)
        except Exception as e:
            logger.error(f"Something went wrong in removing plaid item with id {self.object.id} , error: {str(e)}")
            messages.error(
                self.request,
                "Item could not be removed in Plaid. Please try again.",
            )
        else:
            self.object.delete()
            logger.info("Plaid item deleted successfully")
        finally:
            items = Item.objects.filter(user=self.request.user)
            return render(self.request, "components/bank_cards.html", {"items": items})


class CreatePlaidLinkEvent(LoginRequiredMixin, View):
    """
    Create link events from link creation for troubleshooting purpose.
    """

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(self.request.body)
            link_session_id = data.get("link_session_id")
            event_type = data.get("event_type")
            request_id = data.get("request_id")
            error_type = data.get("error_type")
            error_code = data.get("error_code")

            values = {
                "user_id": request.user.id,
                "event_type": event_type,
                "link_session_id": link_session_id,
            }

            if request_id:
                values["request_id"] = request_id

            if error_type:
                values["error_type"] = error_type

            if error_code:
                values["error_code"] = error_code

            PlaidLinkEvent.objects.create(**values)

            return HttpResponse(status=201)

        except Exception as e:
            logger.error(f"Something went wrong in CreatePlaidLinkEvent {request.user}, error: {str(e)}")
            return HttpResponse(status=500)


class UpdatePlaidItemStatus(LoginRequiredMixin, View):
    """
    Update item's status to good and new_accounts_detected to False.
    """

    def post(self, request, *args, **kwargs):
        try:
            plaid_id = json.loads(self.request.body).get("plaid_id")
            Item.objects.filter(id=plaid_id).update(status=Item.ItemStatusChoices.GOOD, new_accounts_detected=False)
            return JsonResponse(
                {
                    "msg": "Item updated successfully.",
                    "alert": "success",
                },
                status=200,
            )
        except Exception as e:
            logger.error(f"Something went wrong in UpdatePlaidItemStatus {request.user} , error: {str(e)}")
            return JsonResponse(
                {
                    "msg": "Something went wrong while updating your bank account.",
                    "alert": "danger",
                },
                status=500,
            )


class PlaidSandboxItemResetLogin(LoginRequiredMixin, View):
    """
    Forces an Item into an ITEM_LOGIN_REQUIRED state in order to simulate an Item whose login is no longer valid.
    """

    def post(self, request, *args, **kwargs):
        try:
            access_token = Item.objects.first().access_token
            reset_login_request = SandboxItemResetLoginRequest(access_token)
            plaid_config.client.sandbox_item_reset_login(reset_login_request)
            return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"Something went wrong in PlaidSandboxItemResetLogin {request.user} , error: {str(e)}")
            return HttpResponse(status=500)


class PlaidSandboxItemFireWebhook(LoginRequiredMixin, View):
    """
    Sandbox endpoint used to test that code correctly handles webhooks.
    """

    def post(self, request, *args, **kwargs):
        try:
            access_token = Item.objects.first().access_token
            reset_login_request = SandboxItemFireWebhookRequest(access_token, webhook_code="NEW_ACCOUNTS_AVAILABLE")
            plaid_config.client.sandbox_item_fire_webhook(reset_login_request)
            return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"Something went wrong in PlaidSandboxItemFireWebhook {request.user} , error: {str(e)}")
            return HttpResponse(status=500)
