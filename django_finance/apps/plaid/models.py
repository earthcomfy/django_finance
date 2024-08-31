from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_finance.apps.common.models import BaseModel


class Item(BaseModel):
    """
    Item is a Plaid term for a login at a financial institution.
    A single end-user of your application might have accounts at different financial institutions, which means they would have multiple different Items.
    https://plaid.com/docs/quickstart/#create-your-first-item
    """

    class ItemStatusChoices(models.TextChoices):
        GOOD = "GOOD", _("Good")
        BAD = "BAD", _("Bad")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="items", on_delete=models.CASCADE)
    access_token = models.CharField(
        unique=True,
        max_length=255,
        help_text=_("The access token associated with the Item data is being requested for."),
    )
    item_id = models.CharField(
        unique=True,
        max_length=255,
        help_text=_("The item_id value of the Item associated with the returned access_token."),
    )
    institution_id = models.TextField(
        help_text=_("The Plaid Institution ID associated with the Item."),
    )
    institution_name = models.TextField(
        help_text=_("The Plaid Institution name associated with the Item."),
    )
    status = models.CharField(
        max_length=4,
        choices=ItemStatusChoices,
        help_text=_("Status of the item. `Good` or `Bad`"),
    )
    new_accounts_detected = models.BooleanField(
        default=False,
        help_text=_(
            "Set to `True` when Plaid detects a new account for Items created or updated with Account Select v2."
        ),
    )
    transactions_cursor = models.TextField(
        blank=True,
        help_text=_(
            "Cursor used for fetching any future transaction updates after the latest update provided in a transaction response."
        ),
    )

    def __str__(self):
        return f"{self.institution_name} - {self.user}"
