from django.urls import path

from django_finance.apps.accounts.views import ProfileView

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
]
