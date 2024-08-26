import os

from django.conf import settings
from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand


class CustomAppTemplateCommand(TemplateCommand):
    def handle_template(self, template, subdir):
        """
        Loads defined custom app template.
        """
        if template is None:
            return os.path.join(getattr(settings, "BASE_DIR"), "django_finance/config", subdir)
        else:
            if template.startswith("file://"):
                template = template[7:]
            expanded_template = os.path.expanduser(template)
            expanded_template = os.path.normpath(expanded_template)
            if os.path.isdir(expanded_template):
                return expanded_template
            if self.is_url(template):
                absolute_path = self.download(template)
            else:
                absolute_path = os.path.abspath(expanded_template)
            if os.path.exists(absolute_path):
                return self.extract(absolute_path)

        raise CommandError(f"couldn't handle {self.app_or_project} template {template}.")
