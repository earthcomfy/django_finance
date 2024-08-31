import factory

from django_finance.apps.plaid.models import Item
from tests.accounts.factories import UserFactory


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    user = factory.SubFactory(UserFactory)
    access_token = factory.Faker("word")
    item_id = factory.Faker("word")
    institution_id = factory.Faker("word")
    institution_name = factory.Faker("word")
