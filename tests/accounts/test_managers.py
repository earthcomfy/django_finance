import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db

User = get_user_model()


class TestUserManager:
    def test_create_user(self):
        user = User.objects.create_user(email="normal@user.com", password="foo")

        assert user.email == "normal@user.com"
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
        assert getattr(user, "username") is None

    def test_create_user_no_email(self):
        with pytest.raises(ValueError, match="The Email must be set"):
            User.objects.create_user(email=None, password="foo")

    def test_create_superuser(self, mocker):
        admin_user = User.objects.create_superuser(email="super@user.com", password="foo")

        assert admin_user.email == "super@user.com"
        assert admin_user.is_staff
        assert admin_user.is_superuser
        assert admin_user.is_active
        assert getattr(admin_user, "username") is None

    def test_create_superuser_not_staff(self):
        with pytest.raises(ValueError, match="Superuser must have is_staff=True."):
            User.objects.create_superuser(email="super@user.com", password="foo", is_staff=False)

    def test_create_superuser_not_superuser(self):
        with pytest.raises(ValueError, match="Superuser must have is_superuser=True."):
            User.objects.create_superuser(
                email="super@user.com",
                password="foo",
                is_superuser=False,
            )
