import pytest

from tests.accounts.factories import UserFactory


@pytest.fixture
def user():
    """
    Fixture to create a user.

    Returns:
        User: An instance of the User model.
    """
    return UserFactory.create()
