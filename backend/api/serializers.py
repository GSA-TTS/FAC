from rest_framework import serializers

from audit.models import SingleAuditChecklist


class SingleAuditChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = '__all__'
