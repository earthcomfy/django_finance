import pytest

from django_finance.apps.plaid.models import Item

pytestmark = pytest.mark.django_db


class TestItemModel:
    def test_str(self, item: Item):
        assert str(item) == f"{item.institution_name} - {item.user}"
