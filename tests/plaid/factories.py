import factory

from django_finance.apps.plaid.models import Account, Item, PlaidLinkEvent, Transaction
from tests.accounts.factories import UserFactory


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    user = factory.SubFactory(UserFactory)
    access_token = factory.Faker("word")
    item_id = factory.Faker("word")
    institution_id = factory.Faker("word")
    institution_name = factory.Faker("word")


class PlaidLinkEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PlaidLinkEvent

    user_id = factory.Faker("word")
    event_type = factory.Faker(
        "random_element",
        elements=[choice[0] for choice in PlaidLinkEvent.EventTypeChoices.choices],
    )
    link_session_id = factory.Faker("word")
    request_id = factory.Faker("word")
    error_type = factory.Faker("word")
    error_code = factory.Faker("word")


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    item = factory.SubFactory(ItemFactory)
    account_id = factory.Faker("word")
    name = factory.Faker("word")
    account_type = factory.Faker(
        "random_element",
        elements=[choice[0] for choice in Account.ACCOUNT_TYPE_CHOICES.choices],
    )


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    account = factory.SubFactory(AccountFactory)
    transaction_id = factory.Faker("word")
    location = factory.Faker("json")
    pending = factory.Faker("boolean")
    date = factory.Faker("date")
