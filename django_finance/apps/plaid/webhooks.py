import hashlib
import hmac
import logging
import time

from jose import jwt

from django_finance.apps.plaid.models import Item
from django_finance.apps.plaid.services import PlaidDatabaseService
from django_finance.apps.plaid.tasks import update_transactions
from django_finance.apps.plaid.utils import plaid_config
from plaid.model.webhook_verification_key_get_request import (
    WebhookVerificationKeyGetRequest,
)

logger = logging.getLogger(__name__)

# Cache for webhook validation keys.
KEY_CACHE = {}


def verify_webhook(body, headers) -> bool:
    """
    Plaid webhook verification: https://plaid.com/docs/api/webhooks/webhook-verification/
    """
    signed_jwt = headers.get("plaid-verification")
    current_key_id = jwt.get_unverified_header(signed_jwt)["kid"]

    if current_key_id not in KEY_CACHE:
        keys_ids_to_update = [key_id for key_id, key in KEY_CACHE.items() if key["expired_at"] is None]
        keys_ids_to_update.append(current_key_id)

        for key_id in keys_ids_to_update:
            try:
                request = WebhookVerificationKeyGetRequest(key_id=key_id)
                res = plaid_config.client.webhook_verification_key_get(request)
            except Exception:
                continue
            else:
                key = res.to_dict().get("key")
                KEY_CACHE[key_id] = key

    if current_key_id not in KEY_CACHE:
        return False

    key = KEY_CACHE[current_key_id]

    if key["expired_at"] is not None:
        return False

    try:
        claims = jwt.decode(signed_jwt, key, algorithms=["ES256"])
    except Exception:
        return False

    if claims["iat"] < time.time() - 5 * 60:
        return False

    m = hashlib.sha256()
    m.update(body)
    body_hash = m.hexdigest()
    return hmac.compare_digest(body_hash, claims["request_body_sha256"])


def handle_item_webhook(webhook_code, item_id, error) -> None:
    """
    Handle item webhook.
    """

    item = Item.objects.filter(item_id=item_id).first()

    if not item:
        logger.error(f"Item with id {item_id} not found")
        return

    service = PlaidDatabaseService(item)

    if webhook_code == "ERROR":
        if error.get("error_code") == "ITEM_LOGIN_REQUIRED":
            service.update_item_to_bad_state()
            logger.info("PlaidItem updated to bad state.")
        else:
            logger.info(f"WEBHOOK: ITEMS: Plaid item id {item_id}: unhandled ITEM error {error.get('error_message')}")

    elif webhook_code == "PENDING_EXPIRATION":
        service.update_item_to_bad_state()
        logger.info("PlaidItem updated to bad state.")

    elif webhook_code == "NEW_ACCOUNTS_AVAILABLE":
        service.update_item_new_accounts_detected()
        logger.info("PlaidItem new accounts detected.")


def handle_transactions_webhook(webhook_code, item_id) -> None:
    """
    Handle transactions webhook.
    """
    if webhook_code == "SYNC_UPDATES_AVAILABLE":
        item = Item.objects.filter(item_id=item_id).first()
        update_transactions.delay(item.id)
