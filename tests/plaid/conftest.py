import pytest

from tests.plaid.factories import ItemFactory


@pytest.fixture
def item(user):
    return ItemFactory.create(user=user)
