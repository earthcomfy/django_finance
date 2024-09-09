import pytest

from django_finance.apps.plaid.models import Item
from django_finance.apps.plaid.tasks import update_transactions
from django_finance.config.celery import app
from tests.plaid.factories import ItemFactory


@pytest.fixture(scope="module")
def celery_app(request):
    app.conf.update(CELERY_TASK_ALWAYS_EAGER=True)
    return app


@pytest.mark.usefixtures("celery_app")
class TestUpdateTransactions:
    @pytest.fixture
    def setup_mocks(self, mocker):
        return {
            "mock_fetch_transactions": mocker.patch("django_finance.apps.plaid.tasks.PlaidService.fetch_transactions"),
            "mock_fetch_accounts": mocker.patch("django_finance.apps.plaid.tasks.PlaidService.fetch_accounts"),
            "mock_create_or_update_accounts": mocker.patch(
                "django_finance.apps.plaid.tasks.PlaidDatabaseService.create_or_update_accounts"
            ),
            "mock_create_or_update_transactions": mocker.patch(
                "django_finance.apps.plaid.tasks.PlaidDatabaseService.create_or_update_transactions"
            ),
            "mock_delete_transactions": mocker.patch(
                "django_finance.apps.plaid.tasks.PlaidDatabaseService.delete_transactions"
            ),
            "mock_update_item_transaction_cursor": mocker.patch(
                "django_finance.apps.plaid.tasks.PlaidDatabaseService.update_item_transaction_cursor"
            ),
        }

    def test_update_transactions_success(self, create_user, setup_mocks):
        user = create_user()
        item: Item = ItemFactory.create(user=user)

        setup_mocks["mock_fetch_transactions"].return_value = ([], [], [], "new_cursor")
        setup_mocks["mock_fetch_accounts"].return_value = []

        update_transactions(item.id)

        setup_mocks["mock_fetch_transactions"].assert_called_once()
        setup_mocks["mock_fetch_accounts"].assert_called_once()
        setup_mocks["mock_create_or_update_accounts"].assert_called_once_with([])
        setup_mocks["mock_create_or_update_transactions"].assert_called_once_with([])
        setup_mocks["mock_delete_transactions"].assert_called_once_with([])
        setup_mocks["mock_update_item_transaction_cursor"].assert_called_once_with("new_cursor")

    def test_update_transactions_item_not_found(self, create_user, setup_mocks):
        user = create_user()
        item: Item = ItemFactory.create(user=user)

        setup_mocks["mock_fetch_transactions"].return_value = ([], [], [], "new_cursor")
        setup_mocks["mock_fetch_accounts"].return_value = []

        update_transactions(item.id + 1)

        assert setup_mocks["mock_fetch_transactions"].call_count == 0
        assert setup_mocks["mock_fetch_accounts"].call_count == 0
        assert setup_mocks["mock_create_or_update_accounts"].call_count == 0
        assert setup_mocks["mock_create_or_update_transactions"].call_count == 0
        assert setup_mocks["mock_delete_transactions"].call_count == 0
        assert setup_mocks["mock_update_item_transaction_cursor"].call_count == 0

    def test_update_transactions_fail(self, create_user, setup_mocks):
        user = create_user()
        item: Item = ItemFactory.create(user=user)

        setup_mocks["mock_fetch_transactions"].side_effect = Exception("Simulated Exception")
        setup_mocks["mock_fetch_accounts"].return_value = []

        update_transactions(item.id)

        setup_mocks["mock_fetch_transactions"].assert_called_once()
        assert setup_mocks["mock_fetch_accounts"].call_count == 0
        assert setup_mocks["mock_create_or_update_accounts"].call_count == 0
        assert setup_mocks["mock_create_or_update_transactions"].call_count == 0
        assert setup_mocks["mock_delete_transactions"].call_count == 0
        assert setup_mocks["mock_update_item_transaction_cursor"].call_count == 0
