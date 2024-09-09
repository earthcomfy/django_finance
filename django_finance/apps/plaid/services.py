import json
import logging

import plaid
from django_finance.apps.plaid.models import Account, Item, Transaction
from django_finance.apps.plaid.utils import plaid_config
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest

logger = logging.getLogger(__name__)


class PlaidService:
    """
    Plaid API service class.
    """

    def __init__(self, item: Item):
        self.item = item
        self.access_token = item.access_token
        self.cursor = item.transactions_cursor if item.transactions_cursor is not None else ""

    def fetch_transactions(self, retries_left=3) -> tuple[list, list, list, str]:
        """
        Get incremental transaction updates on an Item.
        https://plaid.com/docs/api/products/transactions/#transactionssync
        """
        added, modified, removed = [], [], []
        has_more = True

        if retries_left <= 0:
            logger.info("Too many retries")
            return added, modified, removed, self.cursor

        try:
            while has_more:
                request = TransactionsSyncRequest(access_token=self.access_token, cursor=self.cursor)
                response = plaid_config.client.transactions_sync(request).to_dict()

                added.extend(response["added"])
                modified.extend(response["modified"])
                removed.extend(response["removed"])
                has_more = response["has_more"]
                self.cursor = response["next_cursor"]

            return added, modified, removed, self.cursor

        except plaid.ApiException as e:
            err = json.loads(e.body)
            if err["error_code"] == "TRANSACTIONS_SYNC_MUTATION_DURING_PAGINATION":
                return self.fetch_transactions(retries_left - 1)

            return added, modified, removed, self.cursor

        except Exception as e:
            logger.error(f"Error fetching transactions: {str(e)}")
            return added, modified, removed, self.cursor

    def fetch_accounts(self) -> list:
        """
        Used to retrieve a list of accounts associated with any linked Item.
        https://plaid.com/docs/api/accounts/#accountsget
        """
        try:
            request = AccountsGetRequest(access_token=self.access_token)
            response = plaid_config.client.accounts_get(request)
            return response.to_dict().get("accounts")
        except Exception as e:
            logger.error(f"Error fetching accounts: {str(e)}")
            return []


class PlaidDatabaseService:
    """
    Plaid database service class.
    """

    def __init__(self, item: Item):
        self.item = item

    def create_or_update_accounts(self, accounts) -> None:
        """
        Creates or updates multiple accounts related to a single item.
        """
        for account in accounts:
            defaults = {
                "name": account["name"],
                "account_type": account["type"],
            }

            # Handle balances
            balances = account.get("balances")
            if balances:
                available = balances.get("available")
                current = balances.get("current")
                limit = balances.get("limit")
                iso_currency_code = balances.get("iso_currency_code")
                unofficial_currency_code = balances.get("unofficial_currency_code")

                if available is not None:
                    defaults["available_balance"] = available
                if current is not None:
                    defaults["current_balance"] = current
                if limit is not None:
                    defaults["limit"] = limit
                if iso_currency_code is not None:
                    defaults["iso_currency_code"] = iso_currency_code
                if unofficial_currency_code is not None:
                    defaults["unofficial_currency_code"] = unofficial_currency_code

            # Handle other fields
            for key in ["mask", "official_name", "account_subtype"]:
                val = account.get(key)
                if val is not None:
                    defaults[key] = val

            # Create or update the account
            Account.objects.update_or_create(
                item=self.item,
                account_id=account["account_id"],
                defaults=defaults,
            )

        logger.info(f"{len(accounts)} accounts saved for item {self.item.item_id}")

    def create_or_update_transactions(self, transactions) -> None:
        """
        Creates or updates multiple transactions.
        """
        for transaction in transactions:
            defaults = {
                "location": transaction["location"],
                "pending": transaction["pending"],
                "date": transaction["date"],
            }

            # Handle personal finance category
            category = transaction.get("personal_finance_category")
            if category:
                defaults["primary_personal_finance_category"] = category.get("primary")
                defaults["detailed_personal_finance_category"] = category.get("detailed")
                defaults["confidence_level"] = category.get("confidence_level")

            # Handle other fields
            for key in [
                "amount",
                "iso_currency_code",
                "unofficial_currency_code",
                "check_number",
                "location",
                "name",
                "merchant_name",
                "merchant_entity_id",
                "account_owner",
                "logo_url",
                "website",
                "authorized_date",
                "datetime",
                "authorized_datetime",
                "personal_finance_category_icon_url",
            ]:
                val = transaction.get(key)
                if val is not None:
                    defaults[key] = val

            # Fetch the account associated with the transaction
            account = Account.objects.filter(account_id=transaction["account_id"]).first()

            # Create or update the transaction
            Transaction.objects.update_or_create(
                account=account,
                transaction_id=transaction["transaction_id"],
                defaults=defaults,
            )

        logger.info(f"{len(transactions)} transactions saved to database.")

    def delete_transactions(self, transactions) -> None:
        """
        Removes one or more transactions.
        """
        transaction_ids = [transaction["transaction_id"] for transaction in transactions]
        deleted_count, _ = Transaction.objects.filter(transaction_id__in=transaction_ids).delete()
        logger.info(f"{deleted_count} transactions deleted from database.")

    def update_item_transaction_cursor(self, cursor) -> None:
        """
        Updates the transaction cursor for the item.
        """
        self.item.transactions_cursor = cursor
        self.item.save()
        logger.info("Transaction cursor updated successfully.")

    def update_item_to_bad_state(self) -> None:
        """
        Updates an item to a bad state and creates an alert.
        """
        self.item.status = "Bad"
        self.item.save()

        # TODO - Create an alert

    def update_item_new_accounts_detected(self) -> None:
        """
        Sets `new_accounts_detected` to True and creates an alert.
        """
        self.item.new_accounts_detected = True
        self.item.save()

        # TODO - Create an alert
