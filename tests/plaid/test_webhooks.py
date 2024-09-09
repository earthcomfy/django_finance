import json

import pytest
from django.test import RequestFactory

from django_finance.apps.plaid.models import Item
from django_finance.apps.plaid.views import PlaidWebhook
from django_finance.apps.plaid.webhooks import (
    handle_item_webhook,
    handle_transactions_webhook,
)
from tests.plaid.factories import ItemFactory

pytestmark = pytest.mark.django_db


class TestPlaidWebhook:
    @pytest.fixture
    def setup_mocks(self, mocker):
        return {
            "mock_verify_webhook": mocker.patch("django_finance.apps.plaid.views.verify_webhook"),
            "mock_update_item": mocker.patch(
                "django_finance.apps.plaid.webhooks.PlaidDatabaseService.update_item_to_bad_state"
            ),
            "mock_update_item_new_accounts_detected": mocker.patch(
                "django_finance.apps.plaid.webhooks.PlaidDatabaseService.update_item_new_accounts_detected"
            ),
            "mock_update_transactions": mocker.patch("django_finance.apps.plaid.webhooks.update_transactions.delay"),
            "mock_logger": mocker.patch("django_finance.apps.plaid.webhooks.logger"),
        }

    @pytest.mark.parametrize("webhook_type", ["ITEM", "TRANSACTIONS"])
    def test_valid_webhook_verification(self, setup_mocks, webhook_type):
        setup_mocks["mock_verify_webhook"].return_value = True
        factory = RequestFactory()
        request = factory.post(
            "/finance/webhook/",
            json.dumps({"webhook_type": webhook_type}),
            content_type="application/json",
        )
        headers = {"plaid-verification": "valid_jwt_signature"}
        response = PlaidWebhook.as_view()(request, headers=headers)
        assert response.status_code == 200

    def test_invalid_webhook_verification(self, setup_mocks):
        setup_mocks["mock_verify_webhook"].return_value = False
        factory = RequestFactory()
        request = factory.post(
            "/finance/webhook/",
            json.dumps({"webhook_type": "ITEM"}),
            content_type="application/json",
        )
        headers = {"plaid-verification": "invalid_jwt_signature"}
        response = PlaidWebhook.as_view()(request, headers=headers)
        assert response.status_code == 401

    def test_webhook_exception_handling(self, setup_mocks):
        setup_mocks["mock_verify_webhook"].side_effect = Exception("Test exception")
        factory = RequestFactory()
        request = factory.post("/finance/webhook/", content_type="application/json")
        response = PlaidWebhook.as_view()(request)
        assert response.status_code == 500

    def test_handle_item_webhook_error_code(self, setup_mocks, item: Item):
        error = {
            "error_code": "ITEM_LOGIN_REQUIRED",
            "error_message": "Test error message",
        }
        webhook_code = "ERROR"
        mock_update_item = setup_mocks["mock_update_item"]
        handle_item_webhook(webhook_code, item.item_id, error)
        mock_update_item.assert_called_once()

    def test_handle_item_webhook_unhandled_error(self, setup_mocks, item: Item):
        error = {"error_code": "UNHANDLED_ERROR", "error_message": "Test error message"}
        webhook_code = "ERROR"
        setup_mocks["mock_update_item"]
        mock_logger = setup_mocks["mock_logger"]
        handle_item_webhook(webhook_code, item.item_id, error)
        mock_logger.info.assert_called_once_with(
            f"WEBHOOK: ITEMS: Plaid item id {item.item_id}: unhandled ITEM error {error.get('error_message')}"
        )

    def test_handle_item_webhook_pending_expiration(self, setup_mocks, item: Item):
        webhook_code = "PENDING_EXPIRATION"
        mock_update_item = setup_mocks["mock_update_item"]
        handle_item_webhook(webhook_code, item.item_id, error=None)
        mock_update_item.assert_called_once()

    def test_handle_item_webhook_new_accounts_available(self, setup_mocks, item: Item):
        webhook_code = "NEW_ACCOUNTS_AVAILABLE"
        mock_new_accounts_detected = setup_mocks["mock_update_item_new_accounts_detected"]
        handle_item_webhook(webhook_code, item.item_id, error=None)
        mock_new_accounts_detected.assert_called_once()

    def test_handle_transactions_webhook(self, create_user, setup_mocks):
        user = create_user()
        item: Item = ItemFactory.create(user=user)
        webhook_code = "SYNC_UPDATES_AVAILABLE"
        mock_update_transactions = setup_mocks["mock_update_transactions"]
        handle_transactions_webhook(webhook_code, item.item_id)
        mock_update_transactions.assert_called_once_with(item.id)
