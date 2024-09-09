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

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.institution_name} - {self.user}"


class PlaidLinkEvent(BaseModel):
    """
    Used to log responses from the Plaid API for client requests to the Plaid Link client. This information is useful for troubleshooting.
    """

    class EventTypeChoices(models.TextChoices):
        SUCCESS = "SUCCESS", _("Success")
        EXIT = "EXIT", _("Exit")

    user_id = models.CharField(max_length=250, help_text=_("The ID of the user."))
    event_type = models.CharField(
        max_length=20,
        choices=EventTypeChoices,
        help_text=_("Displayed as `Success` or `Exit` based on response from onSuccess or onExit callbacks."),
    )
    link_session_id = models.TextField(
        help_text=_("A unique identifier associated with a user's actions and events through the Link flow."),
    )
    request_id = models.TextField(
        blank=True,
        help_text=_("A unique identifier for the request, which can be used for troubleshooting."),
    )
    error_type = models.TextField(
        blank=True,
        help_text=_("A broad categorization of the error."),
    )
    error_code = models.TextField(
        blank=True,
        help_text=_("The particular error code. Each error_type has a specific set of error_codes."),
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"LinkEvent: user_id={self.user_id}, type={self.event_type}"


class Account(BaseModel):
    """
    Used to store the accounts associated with each item.
    """

    class ACCOUNT_TYPE_CHOICES(models.TextChoices):
        INVESTMENT = "investment", _("Investment")
        CREDIT = "credit", _("Credit")
        DEPOSITORY = "depository", _("Depository")
        LOAN = "loan", _("Loan")
        BROKERAGE = "brokerage", _("Brokerage")
        OTHER = "other", _("Other")

    item = models.ForeignKey(Item, related_name="accounts", on_delete=models.CASCADE)
    account_id = models.CharField(
        unique=True,
        max_length=255,
        help_text=_("Plaid’s unique identifier for the account."),
    )
    name = models.CharField(
        max_length=250,
        help_text=_("The name of the account, either assigned by the user or by the financial institution itself."),
    )
    mask = models.CharField(
        max_length=4,
        blank=True,
        help_text=_("The last 2-4 alphanumeric characters of an account's official account number."),
    )
    official_name = models.TextField(
        blank=True,
        help_text=_("The official name of the account as given by the financial institution."),
    )
    available_balance = models.DecimalField(
        max_digits=65,
        decimal_places=30,
        blank=True,
        null=True,
        help_text=_(
            "The amount of funds available to be withdrawn from the account, as determined by the financial institution."
        ),
    )
    current_balance = models.DecimalField(
        max_digits=65,
        decimal_places=30,
        blank=True,
        null=True,
        help_text=_("The total amount of funds in or owed by the account."),
    )
    limit = models.DecimalField(
        max_digits=65,
        decimal_places=30,
        blank=True,
        null=True,
        help_text=_("For credit-type accounts, this represents the credit limit."),
    )
    iso_currency_code = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("The ISO-4217 currency code of the balance."),
    )
    unofficial_currency_code = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("The unofficial currency code associated with the balance."),
    )
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        help_text=_("Account types. Possible values: investment, credit, depository, loan, brokerage, other"),
    )
    account_subtype = models.CharField(max_length=250, blank=True, help_text=_("Account subtype"))

    def __str__(self):
        return f"Account {self.account_id}, Item {self.item}"


class Transaction(BaseModel):
    """
    Used to store the transactions associated with each account.
    """

    class TRANSACTION_CATEGORY_CONFIDENCE_LEVEL(models.TextChoices):
        UNKNOWN = "unknown", _("Unknown")
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        VERY_HIGH = "very_high", _("Very High")

    account = models.ForeignKey(Account, related_name="transactions", on_delete=models.CASCADE)
    transaction_id = models.CharField(
        unique=True,
        max_length=255,
        help_text=_(
            "The unique ID of the transaction. Like all Plaid identifiers, the transaction_id is case sensitive."
        ),
    )
    amount = models.DecimalField(
        max_digits=65,
        decimal_places=30,
        blank=True,
        null=True,
        help_text=_(
            "The settled value of the transaction, denominated in the transactions's currency, as stated in iso_currency_code or unofficial_currency_code."
        ),
    )
    iso_currency_code = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("The ISO-4217 currency code of the balance."),
    )
    unofficial_currency_code = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("The unofficial currency code associated with the balance."),
    )
    check_number = models.TextField(
        blank=True,
        help_text=_("The check number of the transaction. This field is only populated for check transactions."),
    )
    location = models.JSONField(help_text=_("A representation of where a transaction took place."))
    name = models.TextField(blank=True, help_text=_("The merchant name or transaction description."))
    merchant_name = models.TextField(
        blank=True,
        help_text=_("The merchant name, as enriched by Plaid from the name field."),
    )
    merchant_entity_id = models.TextField(
        blank=True,
        help_text=_("A unique, stable, Plaid-generated ID that maps to the merchant."),
    )
    pending = models.BooleanField(help_text=_("When true, identifies the transaction as pending or unsettled."))
    account_owner = models.TextField(
        blank=True,
        help_text=_(
            "The name of the account owner. This field is not typically populated and only relevant when dealing with sub-accounts."
        ),
    )
    logo_url = models.URLField(
        blank=True,
        null=True,
        help_text=_(
            "The URL of a logo associated with this transaction, if available. The logo will always be 100×100 pixel PNG file."
        ),
    )
    website = models.TextField(
        blank=True,
        help_text=_("The website associated with this transaction, if available."),
    )
    date = models.DateField(
        help_text=_(
            "For pending transactions, the date that the transaction occurred; for posted transactions, the date that the transaction posted."
        )
    )
    authorized_date = models.DateField(
        blank=True,
        null=True,
        help_text=_(
            "The date that the transaction was authorized. For posted transactions, the date field will indicate the posted date, "
            "but authorized_date will indicate the day the transaction was authorized by the financial institution. "
            "If presenting transactions to the user in a UI, the authorized_date, when available, is generally preferable "
            "to use over the date field for posted transactions, as it will generally represent the date the user actually made the transaction."
        ),
    )
    datetime = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Date and time when a transaction was posted."),
    )
    authorized_datetime = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_(
            "The date and time that the transaction was authorized. For posted transactions, the datetime field will indicate the posted date, "
            "but authorized_date will indicate the day the transaction was authorized by the financial institution. "
            "If presenting transactions to the user in a UI, the authorized_date, when available, is generally preferable "
            "to use over the date field for posted transactions, as it will generally represent the date the user actually made the transaction."
        ),
    )
    primary_personal_finance_category = models.TextField(
        blank=True,
        help_text=_("A high level category that communicates the broad category of the transaction."),
    )
    detailed_personal_finance_category = models.TextField(
        blank=True,
        help_text=_(
            "A granular category conveying the transaction's intent. This field can also be used as a unique identifier for the category."
        ),
    )
    confidence_level = models.CharField(
        max_length=200,
        blank=True,
        choices=TRANSACTION_CATEGORY_CONFIDENCE_LEVEL,
        help_text=_(
            "A description of how confident we are that the provided categories accurately describe the transaction intent."
        ),
    )
    personal_finance_category_icon_url = models.URLField(
        blank=True,
        null=True,
        help_text=_(
            "The URL of an icon associated with the primary personal finance category. The icon will always be 100×100 pixel PNG file."
        ),
    )

    class Meta:
        ordering = ("-date",)

    def __str__(self):
        return f"Transaction {self.transaction_id}, Account {self.account}"
