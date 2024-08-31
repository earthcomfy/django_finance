import uuid

from django.db import models

from django_finance.apps.common.managers import BaseModelManager


class BaseModel(models.Model):
    """
    Base model for common fields and methods.
    """

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True, help_text="Used for soft deleting records.")

    objects = BaseModelManager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_active = False
        self.save()

    def restore(self):
        self.is_active = True
        self.save()
