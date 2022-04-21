from audit.models import SingleAuditChecklist
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import EligibilitySerializer, SingleAuditChecklistSerializer, UEISerializer


class SACViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows SACs to be viewed.
    """
    allowed_methods = ['GET']
    queryset = SingleAuditChecklist.objects.all()
    serializer_class = SingleAuditChecklistSerializer

    def get_view_name(self):
        return 'SF-SAC'


class EligibilityFormView(APIView):
    """
    Accepts SF-SAC eligibility form responses, determines eligibility, and returns either
    messages describing ineligibility or a reference to the next step in submitted an SF-SAC.
    """
    def post(self, request):
        serializer = EligibilitySerializer(data=request.data)
        if serializer.is_valid():
            next_step = reverse('general-info')
            request.session['sac'] = request.data
            return Response({'eligible': True, 'next': next_step})
        return Response({'eligible': False, 'errors': serializer.errors})


class UEIValidationFormView(APIView):
    """
    Accepts UEI to validate and returns either a message describing the validation errors, or valid.
    """
    def post(self, request):
        serializer = UEISerializer(data=request.data)
        if serializer.is_valid():
            return Response({'valid': True})
        return Response({'valid': False, 'errors': serializer.errors})


class GeneralInfoView(APIView):

    def get(self, request):
        return Response({'ok': True})
