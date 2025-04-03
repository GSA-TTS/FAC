from api.serializers.access import (
    AccessListSerializer,
    AccessAndSubmissionSerializer,
    AccessSerializer,
    CERTIFIERS_HAVE_DIFFERENT_EMAILS,
)
from api.serializers.audit import AuditSerializer, SingleAuditChecklistSerializer
from api.serializers.auditee import AuditeeInfoSerializer
from api.serializers.eligibility import EligibilitySerializer
from api.serializers.uei import UEISerializer

serializers_list = [
    AccessAndSubmissionSerializer,
    AccessListSerializer,
    AccessSerializer,
    AuditeeInfoSerializer,
    AuditSerializer,
    EligibilitySerializer,
    SingleAuditChecklistSerializer,
    UEISerializer,
]

constants = [CERTIFIERS_HAVE_DIFFERENT_EMAILS]
