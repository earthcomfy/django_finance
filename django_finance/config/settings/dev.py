from .base import *  # noqa: F403

INSTALLED_APPS += [  # noqa: F405
    "debug_toolbar",
    "django_browser_reload",
]

MIDDLEWARE += [  # noqa: F405
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
