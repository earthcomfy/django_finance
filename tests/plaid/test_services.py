import plaid
import pytest

from django_finance.apps.plaid.models import Account, Item, Transaction
from django_finance.apps.plaid.services import PlaidDatabaseService, PlaidService
from tests.plaid.dummy_data import (
    ACCOUNTS,
    ACCOUNTS_RESPONSE,
    TRANSACTIONS_ADDED,
    TRANSACTIONS_CURSOR,
    TRANSACTIONS_MODIFIED,
    TRANSACTIONS_REMOVED,
    TRANSACTIONS_SYNC_RESPONSE,
)
from tests.plaid.factories import AccountFactory, ItemFactory, TransactionFactory


class TestPlaidService:
    class MockTransactionsSyncResponse:
        def to_dict(self):
            return TRANSACTIONS_SYNC_RESPONSE

    class MockAccountsResponse:
        def to_dict(self):
            return ACCOUNTS_RESPONSE

    @pytest.fixture
    def api_exception(self):
        def make_api_exception(error_code):
            return type(
                "",
                (),
                {
                    "status": 500,
                    "reason": "Internal Server Error",
                    "data": f'{{"error_code": "{error_code}"}}',
                    "getheaders": lambda self: [("Content-Type", "application/json")],
                },
            )()

        return make_api_exception

    @pytest.fixture
    def setup_mocks(self, mocker):
        return {
            "mock_transactions_sync": mocker.patch(
                "django_finance.apps.plaid.services.plaid_config.client.transactions_sync"
            ),
            "mock_accounts_get": mocker.patch("django_finance.apps.plaid.services.plaid_config.client.accounts_get"),
        }

    def test_fetch_transactions_success(self, create_user, setup_mocks):
        user = create_user()
        item: Item = ItemFactory.create(user=user)
        setup_mocks["mock_transactions_sync"].return_value = self.MockTransactionsSyncResponse()
        added, modified, removed, cursor = PlaidService(item).fetch_transactions()
        assert added == TRANSACTIONS_ADDED
        assert modified == TRANSACTIONS_MODIFIED
        assert removed == TRANSACTIONS_REMOVED
        assert cursor == TRANSACTIONS_CURSOR

    def test_fetch_transactions_retry_on_failure(self, create_user, api_exception, setup_mocks):
        user = create_user()
        item: Item = ItemFactory.create(user=user)
        exception = plaid.ApiException(
            status=500,
            reason="Internal Server Error",
            http_resp=api_exception("TRANSACTIONS_SYNC_MUTATION_DURING_PAGINATION"),
        )
        setup_mocks["mock_transactions_sync"].side_effect = [
            exception,
            self.MockTransactionsSyncResponse(),
        ]
        added, modified, removed, cursor = PlaidService(item).fetch_transactions()
        assert added == TRANSACTIONS_ADDED
        assert modified == TRANSACTIONS_MODIFIED
        assert removed == TRANSACTIONS_REMOVED
        assert cursor == TRANSACTIONS_CURSOR

    def test_fetch_transactions_max_retries(self, create_user, setup_mocks):
        user = create_user()
        item: Item = ItemFactory.create(user=user)
        setup_mocks["mock_transactions_sync"].side_effect = self.MockTransactionsSyncResponse()
        added, modified, removed, cursor = PlaidService(item).fetch_transactions(retries_left=0)
        added, modified, removed, cursor = PlaidService(item).fetch_transactions()
        assert added == modified == removed == []
        assert cursor == ""

    @pytest.mark.parametrize(
        "exception",
        [
            Exception("Simulated Exception"),
            lambda api_exception: plaid.ApiException(
                status=500,
                reason="Internal Server Error",
                http_resp=api_exception("ERROR_CODE"),
            ),
        ],
    )
    def test_fetch_transactions_fail(self, create_user, api_exception, exception, setup_mocks):
        user = create_user()
        item: Item = ItemFactory.create(user=user)

        if callable(exception):
            exception_instance = exception(api_exception)
        else:
            exception_instance = exception

        setup_mocks["mock_transactions_sync"].side_effect = exception_instance
        added, modified, removed, cursor = PlaidService(item).fetch_transactions()
        assert added == modified == removed == []
        assert cursor == ""

    def test_fetch_accounts_success(self, create_user, setup_mocks):
        user = create_user()
        item: Item = ItemFactory.create(user=user)
        setup_mocks["mock_accounts_get"].return_value = self.MockAccountsResponse()
        assert PlaidService(item).fetch_accounts() == ACCOUNTS

    def test_fetch_accounts_fail(self, create_user, setup_mocks):
        user = create_user()
        item: Item = ItemFactory.create(user=user)
        setup_mocks["mock_accounts_get"].side_effect = Exception("Simulated Exception")
        assert PlaidService(item).fetch_accounts() == []


class TestPlaidDatabaseService:
    def test_create_or_update_accounts(self, create_user):
        user = create_user()
        item: Item = ItemFactory.create(user=user)
        PlaidDatabaseService(item).create_or_update_accounts(ACCOUNTS)
        assert Account.objects.count() == len(ACCOUNTS)

    def test_create_or_update_transactions(self, create_user):
        user = create_user()
        item: Item = ItemFactory.create(user=user)
        AccountFactory.create(item=item, account_id=TRANSACTIONS_ADDED[0]["account_id"])
        PlaidDatabaseService(item).create_or_update_transactions(TRANSACTIONS_ADDED)
        assert Transaction.objects.count() == len(TRANSACTIONS_ADDED)

    def test_delete_transactions(self, create_user):
        user = create_user()
        item: Item = ItemFactory.create(user=user)
        account: Account = AccountFactory.create(item=item)
        transaction: Transaction = TransactionFactory.create(account=account)
        removed = [{"transaction_id": transaction.transaction_id}]
        PlaidDatabaseService(item).delete_transactions(removed)
        assert not Transaction.objects.filter(transaction_id=transaction.transaction_id).exists()

    def test_update_item_transaction_cursor(self, create_user):
        user = create_user()
        item: Item = ItemFactory.create(user=user)
        PlaidDatabaseService(item).update_item_transaction_cursor(cursor="last_cursor")
        assert item.transactions_cursor == "last_cursor"

    def test_update_item_to_bad_state(self, create_user):
        user = create_user()
        item: Item = ItemFactory.create(user=user)
        PlaidDatabaseService(item).update_item_to_bad_state()
        item.refresh_from_db()
        assert item.status == "Bad"

    def test_update_item_new_accounts_detected(self, create_user):
        user = create_user()
        item: Item = ItemFactory.create(user=user)
        PlaidDatabaseService(item).update_item_new_accounts_detected()
        item.refresh_from_db()
        assert item.new_accounts_detected is True
