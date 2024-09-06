from django.contrib import admin

from django_finance.apps.plaid.models import Item, PlaidLinkEvent

admin.site.register(Item)
admin.site.register(PlaidLinkEvent)
