from rest_framework import serializers

from audit.models import SingleAuditChecklist, Audit


# TODO: Update Post SOC Launch -> Delete
class SingleAuditChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = "__all__"


class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audit
        fields = "__all__"
