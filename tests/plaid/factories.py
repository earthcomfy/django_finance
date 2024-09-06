import factory

from django_finance.apps.plaid.models import Item, PlaidLinkEvent
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
