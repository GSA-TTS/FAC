from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from jwt import InvalidTokenError

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import LoginGovUser

import string
import random


class JWTUpsertAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id_claim = settings.SIMPLE_JWT['USER_ID_CLAIM']

            user_id = validated_token[user_id_claim]
            email = validated_token['email']
        except KeyError:
            raise InvalidTokenError(_("Token contained no recognizable user identification"))

        try:
            # find an existing user
            login_user = LoginGovUser.objects.get(**{"login_id": user_id})
            user = login_user.user
        except LoginGovUser.DoesNotExist:
            # didn't find one, create a new user

            # generate a random password
            password = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))

            # create auth_user
            user = self.user_model.objects.create_user(email, email, password)

            # create and associate LoginGovUser instance
            login_user = LoginGovUser.objects.create(**{
                "user": user,
                "login_id": user_id
            })

        user.last_login = timezone.now()
        user.save()

        return user


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        try:
            user, token = super().authenticate(request)
        except TypeError:
            raise AuthenticationFailed('Authentication failed!')

        # determine the age of this token
        now = timezone.now()
        created = token.created
        age = (now - created).total_seconds()
        ttl = settings.TOKEN_AUTH['TOKEN_TTL']

        if (age > ttl):
            raise AuthenticationFailed('Token expired!')

        return user, token
