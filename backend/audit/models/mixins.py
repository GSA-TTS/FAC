from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CreatedMixin(models.Model):
    """
    Adds basic created_by, created_at fields to a record
    """

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class UpdatedMixin(models.Model):
    """
    Adds basic updated_by, updated_at fields to a record
    """

    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
