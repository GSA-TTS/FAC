from rest_framework import serializers

from audit.models import SingleAuditChecklist


class EligibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = ['user_provided_organization_type', 'met_spending_threshold', 'is_usa_based']

    def validate(self, data):
        if not (data['met_spending_threshold'] and data['is_usa_based']):
            raise serializers.ValidationError("Must be USA based and have met spending threshold")
        return data


class UEISerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = ['uei']


class SingleAuditChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = '__all__'
