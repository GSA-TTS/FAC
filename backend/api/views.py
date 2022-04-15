from audit.models import SingleAuditChecklist
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import EligibilitySerializer, SingleAuditChecklistSerializer


class SACViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows SACs to be viewed or edited.
    """
    allowed_methods = ['GET']
    queryset = SingleAuditChecklist.objects.all()
    serializer_class = SingleAuditChecklistSerializer

    def get_view_name(self):
        return 'SF-SAC'


class EligibilityFormView(APIView):

    def post(self, request):
        serializer = EligibilitySerializer(data=request.data)
        if serializer.is_valid():
            # Store in user session
            # request.session['sac'] = request.data
            # return success
            pass
        return Response(serializer.errors)
