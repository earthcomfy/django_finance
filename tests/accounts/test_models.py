import pytest

pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_str(self, user):
        assert str(user) == user.email
