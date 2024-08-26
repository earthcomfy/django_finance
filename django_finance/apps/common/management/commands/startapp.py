import os

from django.conf import settings

from django_finance.apps.common.management.templates import CustomAppTemplateCommand


class Command(CustomAppTemplateCommand):
    help = (
        "Creates a Django app directory structure for the given app name in "
        "the current directory or optionally in the given directory."
    )
    missing_args_message = "You must provide an application name."

    def handle(self, **options):
        app_name = options.pop("name")
        target = None
        base_dir = getattr(settings, "BASE_DIR")
        if not options.pop("directory"):
            app_dir = os.path.join(base_dir, "django_finance/apps", app_name)
            os.mkdir(app_dir)
            target = app_dir
        super().handle("app", app_name, target, **options)
