from rest_framework import viewsets

from audit.models import SingleAuditChecklist
from .serializers import SingleAuditChecklistSerializer


class SACViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows SACs to be viewed or edited.
    """
    allowed_methods = ['GET']
    queryset = SingleAuditChecklist.objects.all()
    serializer_class = SingleAuditChecklistSerializer

    def get_view_name(self):
        return 'SF-SAC'
