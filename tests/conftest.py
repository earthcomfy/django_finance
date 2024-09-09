import pytest
from django.test import Client

from tests.accounts.factories import UserFactory


@pytest.fixture
def user():
    """
    Fixture to create a user.

    Returns:
        User: An instance of the User model.
    """
    return UserFactory.create()


@pytest.fixture
def client():
    """
    Fixture to create a Django test client.

    Returns:
        Client: An instance of the Django test client.
    """

    return Client()


@pytest.fixture
def test_password() -> str:
    """
    Fixture function that returns a test password.

    Returns:
        str: The test password.
    """
    return "123test"


@pytest.fixture
def create_user(django_user_model, test_password):
    """
    Fixture for creating a user in Django.

    Returns:
    - make_user: A function that takes an email as input and creates a user with the given email and test password.
    """

    def _make_user(email="test@example.com"):
        return django_user_model.objects.create_user(email=email, password=test_password)

    return _make_user


@pytest.fixture
def login(client, create_user, test_password):
    """
    Fixture for logging in a client.

    Returns:
    - A function that logs in a client with the specified email and password.
    """

    def _make_login(email="test@example.com"):
        user = create_user(email)
        client.login(email=user.email, password=test_password)
        return client, user

    return _make_login
