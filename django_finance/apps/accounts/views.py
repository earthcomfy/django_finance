from django.views.generic import TemplateView


class ProfileView(TemplateView):
    template_name = "account/profile.html"
