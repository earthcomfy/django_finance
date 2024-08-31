from django.db import models


class BaseModelManager(models.Manager):
    """
    A custom manager for the base model.

    This manager filters the queryset to only include active records.

    """

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
