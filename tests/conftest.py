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
