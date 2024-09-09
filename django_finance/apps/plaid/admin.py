from django.contrib import admin

from django_finance.apps.plaid.models import Account, Item, PlaidLinkEvent, Transaction

admin.site.register(PlaidLinkEvent)


class PlaidTransactionInline(admin.TabularInline):
    model = Transaction
    extra = 1


class AccountInline(admin.TabularInline):
    model = Account
    extra = 1


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = [AccountInline]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    inlines = [PlaidTransactionInline]
    list_display = ("account_id", "name", "account_type", "item")
    search_fields = ("account_id", "name", "account_type")


@admin.register(Transaction)
class PlaidTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "amount", "date", "account")
    search_fields = ("transaction_id", "name", "merchant_name")
    list_filter = ("date", "pending", "confidence_level")
