from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from jwt import InvalidTokenError

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import LoginGovUser

from audit.models import Access

import logging
import string
import random

logger = logging.getLogger(__name__)


def claim_audit_access(user, all_emails):
    access_invites = (
        Access.objects.filter(user_id=None)
        .filter(email__in=all_emails)
        .update(user_id=user.id)
    )
    logger.debug(f"{user.email} granted access to {access_invites} new audits")


class JWTUpsertAuthentication(JWTAuthentication):
    def get_or_create_auth_user(self, email, all_emails):
        # find all Users where email is in LoginGov all_emails
        users = self.user_model.objects.filter(email__in=all_emails)

        if users.count() > 1:
            # more than one found, take the one that matches the LoginGov primary email
            try:
                user = users.get(email=email)
            except self.user_model.DoesNotExist:
                # none of the Users use the LoginGov primary email, take the first one
                user = users[0]
        elif users.count() == 1:
            # found a single User match
            user = users[0]
        else:
            # didn't find an existing User, create one

            # generate a random password
            password = "".join(
                random.SystemRandom().choice(string.ascii_letters + string.digits)
                for _ in range(32)
            )

            user = self.user_model.objects.create_user(email, email, password) 

        return user

    def get_user(self, validated_token):
        try:
            user_id_claim = settings.SIMPLE_JWT["USER_ID_CLAIM"]

            user_id = validated_token[user_id_claim]
            email = validated_token["email"]
            all_emails = validated_token["all_emails"]
        except KeyError:
            raise InvalidTokenError(
                _("Token contained no recognizable user identification")
            )

        try:
            # find an existing user
            login_user = LoginGovUser.objects.get(**{"login_id": user_id})
            user = login_user.user

            logger.debug(f"found existing user record for {user.email}")
        except LoginGovUser.DoesNotExist:
            user = self.get_or_create_auth_user(email, all_emails)

            logger.debug(f"created new user record for {user.email}")

            # create and associate LoginGovUser instance
            login_user = LoginGovUser.objects.create(
                **{"user": user, "login_id": user_id}
            )

        user.last_login = timezone.now()
        user.save()

        # claim any pending audit accesses associated with this user's email addresses
        claim_audit_access(user, all_emails)

        return user


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        try:
            user, token = super().authenticate(request)
        except TypeError:
            raise AuthenticationFailed("Authentication failed!")

        # determine the age of this token
        now = timezone.now()
        created = token.created
        age = (now - created).total_seconds()
        ttl = settings.TOKEN_AUTH["TOKEN_TTL"]

        if age > ttl:
            raise AuthenticationFailed("Token expired!")

        return user, token
