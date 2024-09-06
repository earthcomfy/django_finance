import pytest

from tests.plaid.factories import ItemFactory, PlaidLinkEventFactory


@pytest.fixture
def item(user):
    return ItemFactory.create(user=user)


@pytest.fixture
def link_event():
    return PlaidLinkEventFactory.create()
