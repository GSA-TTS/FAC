from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .auth import JWTUpsertAuthentication


class AuthToken(ObtainAuthToken):
    authentication_classes = [JWTUpsertAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # delete previously created token, if one exists
        try:
            prior_token = Token.objects.get(user=request.user)
        except Token.DoesNotExist:
            prior_token = None

        if prior_token:
            prior_token.delete()

        token = Token.objects.create(user=request.user)
        return Response({"token": token.key})
