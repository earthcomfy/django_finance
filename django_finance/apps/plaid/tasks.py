import logging

from celery import shared_task

from django_finance.apps.plaid.models import Item
from django_finance.apps.plaid.services import PlaidDatabaseService, PlaidService

logger = logging.getLogger(__name__)


@shared_task(queue="long")
def update_transactions(id: int):
    """
    Handles the fetching and storing of new, modified, and removed transactions.
    """
    try:
        item = Item.objects.filter(id=id).first()

        if not item:
            logger.error(f"Item with id {id} not found")
            return

        service = PlaidService(item)

        added, modified, removed, cursor = service.fetch_transactions()
        accounts = service.fetch_accounts()

        db_service = PlaidDatabaseService(item)

        db_service.create_or_update_accounts(accounts)
        db_service.create_or_update_transactions(added + modified)
        db_service.delete_transactions(removed)
        db_service.update_item_transaction_cursor(cursor)

    except Exception as e:
        logger.error(f"Something went wrong in update_transactions for plaid item {id}, {str(e)}")
