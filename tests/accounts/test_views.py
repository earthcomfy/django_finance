import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestProfileView:
    def test_profile_view_uses_correct_template(self, client):
        response = client.get(reverse("profile"))
        assert response.status_code == 200
        assert "account/profile.html" in (t.name for t in response.templates)
