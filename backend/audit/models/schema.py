import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils import timezone

from audit.models.constants import AUDIT_TYPE, AUDIT_TYPE_CODES

logger = logging.getLogger(__name__)

User = get_user_model()
class SchemaManager(models.Manager):
    def get_current_schema(self, audit_type: AUDIT_TYPE):
        query = (Q(audit_type=audit_type) &
                 (Q(valid_start__lte=timezone.now()) &
                             (Q(valid_end__gte=timezone.now()) |
                              Q(valid_end__isnull=True))))
        return self.filter(query).first()

class Schema(models.Model):
    """
    Object representing a Audit Schema. The Audit schema is in charge of validating
    an audit at a given point of time. In other words, as the schemas change over time
    an old audit can be re-evaluated against the old rules.
    """
    objects = SchemaManager()

    version = models.CharField(max_length=35,
                               unique=True,
                               db_index=True,
                               editable=False)
    schema = models.JSONField()
    audit_type = models.CharField(max_length=20, choices=AUDIT_TYPE_CODES, blank=False, null=False)
    description = models.TextField()
    valid_start = models.DateTimeField()
    valid_end = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Schema("version={self.version}", "audit_type={self.audit_type}", valid_start={self.valid_start}, valid_end={self.valid_end})'

