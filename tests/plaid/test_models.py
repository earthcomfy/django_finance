import pytest

from django_finance.apps.plaid.models import Item, PlaidLinkEvent

pytestmark = pytest.mark.django_db


class TestItemModel:
    def test_str(self, item: Item):
        assert str(item) == f"{item.institution_name} - {item.user}"


class TestPlaidLinkEventModel:
    def test_str(self, link_event: PlaidLinkEvent):
        assert f"LinkEvent: user_id={link_event.user_id}, type={link_event.event_type}" == str(link_event)
