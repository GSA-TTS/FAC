from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from audit.models import SingleAuditChecklist


SPENDING_THRESHOLD = _("The FAC only accepts submissions from non-Federal entities that spend $750,000 or more in federal awards during its audit period (fiscal period begin dates on or after 12/26/2014) in accordance with Uniform Guidance")
USA_BASED = _("The FAC only accepts submissions from U.S.-based entities")
USER_PROVIDED_ORG_TYPE = _("The FAC only accepts submissions from States, Local governments, Indian tribes or Tribal organizations, Institutions of higher education (IHEs), and Non-profits")


class EligibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = ['user_provided_organization_type', 'met_spending_threshold', 'is_usa_based']

    def validate_is_usa_based(self, value):
        if not value:
            raise serializers.ValidationError(USA_BASED)
        return value

    def validate_met_spending_threshold(self, value):
        if not value:
            raise serializers.ValidationError(SPENDING_THRESHOLD)
        return value

    def validate_user_provided_organization_type(self, value):
        if value == 'none':
            raise serializers.ValidationError(USER_PROVIDED_ORG_TYPE)
        return value


class UEISerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = ['uei']


class SingleAuditChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = '__all__'
