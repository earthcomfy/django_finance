from django.urls import path

from django_finance.apps.plaid.views import (
    AccountsInItemView,
    CreatePlaidLinkEvent,
    CreatePlaidLinkToken,
    DashboardView,
    ExchangePlaidPublicAccessToken,
    PlaidRemoveItemView,
    PlaidSandboxItemFireWebhook,
    PlaidSandboxItemResetLogin,
    PlaidWebhook,
    UpdatePlaidItemStatus,
)

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("item-accounts/<int:pk>", AccountsInItemView.as_view(), name="account_list"),
    path("create-link-token/", CreatePlaidLinkToken.as_view(), name="create_link_token"),
    path(
        "exchange-public-token/",
        ExchangePlaidPublicAccessToken.as_view(),
        name="exchange_public_token",
    ),
    path("create-link-event/", CreatePlaidLinkEvent.as_view(), name="create_link_event"),
    path(
        "update-item-status/",
        UpdatePlaidItemStatus.as_view(),
        name="update_item_status",
    ),
    path(
        "remove/<int:pk>/",
        PlaidRemoveItemView.as_view(),
        name="remove_item",
    ),
    path("reset-login/", PlaidSandboxItemResetLogin.as_view(), name="reset_login"),
    path("fire-webhook/", PlaidSandboxItemFireWebhook.as_view(), name="fire_webhook"),
    path("webhook/", PlaidWebhook.as_view(), name="plaid_webhook"),
]
