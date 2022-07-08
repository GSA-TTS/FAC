from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from jwt import InvalidTokenError

from model_bakery import baker

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from .auth import ExpiringTokenAuthentication, JWTUpsertAuthentication
from .models import LoginGovUser

from datetime import timedelta
from uuid import uuid4

User = get_user_model()


class JwtUpsertAuthenticationTests(TestCase):
    def test_no_user_id_claim(self):
        """
        if token contains no user ID claim, an exception should be raised
        """
        auth = JWTUpsertAuthentication()
        token = {}

        self.assertRaises(InvalidTokenError, auth.get_user, token)

    def test_no_email_claim(self):
        """
        if token contains no email claim, an exception should be raised
        """
        auth = JWTUpsertAuthentication()

        login_id = str(uuid4())

        token = {"sub": login_id}

        self.assertRaises(InvalidTokenError, auth.get_user, token)

    def test_new_user(self):
        """
        if no internal user or LoginGovUser exist, new ones should be created
        """
        auth = JWTUpsertAuthentication()

        login_id = str(uuid4())

        token = {"sub": login_id, "email": "test-email@test.test"}

        user = auth.get_user(token)

        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test-email@test.test")
        self.assertEqual(user.username, "test-email@test.test")
        self.assertIsNotNone(user.last_login)

        # an instance of LoginGovUser should exist for the newly created user
        login_user = LoginGovUser.objects.get(user=user)

        self.assertIsNotNone(login_user)
        self.assertEqual(login_user.user_id, user.id)
        self.assertEqual(login_user.login_id, login_id)

    def test_existing_user(self):
        """
        if internal user and LoginGovUser exist, existing user should be returned
        """
        existing_user = baker.make(User)
        login_id = str(uuid4())

        baker.make(LoginGovUser, user=existing_user, login_id=login_id)

        auth = JWTUpsertAuthentication()

        token = {"sub": login_id, "email": "existing-user@test.test"}

        user = auth.get_user(token)

        self.assertIsNotNone(user)
        self.assertEqual(user.id, existing_user.id)
        self.assertEqual(user.username, existing_user.username)
        self.assertEqual(user.email, existing_user.email)

    def test_existing_auth_user(self):
        """
        if internal user exists, but has no associated LoginGovUser, LoginGovUser should be created
        """
        existing_user = baker.make(User)
        login_id = str(uuid4())

        auth = JWTUpsertAuthentication()

        token = {"sub": login_id, "email": existing_user.email}

        user = auth.get_user(token)

        self.assertIsNotNone(user)
        self.assertEqual(user.id, existing_user.id)
        self.assertEqual(user.username, existing_user.username)
        self.assertEqual(user.email, existing_user.email)


class ExpiringTokenAuthenticationTests(TestCase):
    def test_valid_token(self):
        """
        a newly-created (not expired) token should be valid
        """
        auth = ExpiringTokenAuthentication()

        user = baker.make(User)
        token = baker.make(Token, user=user)

        factory = RequestFactory()
        request = factory.get("/api", **{"HTTP_AUTHORIZATION": "Token " + token.key})

        auth.authenticate(request)

    def test_expired_token(self):
        """
        an expired token should be invalid
        """
        auth = ExpiringTokenAuthentication()
        ttl = settings.TOKEN_AUTH["TOKEN_TTL"]

        created = timezone.now() - timedelta(seconds=ttl + 1)

        user = baker.make(User)
        token = baker.make(Token, user=user)

        token.created = created
        token.save()

        factory = RequestFactory()
        request = factory.get("/api", **{"HTTP_AUTHORIZATION": "Token " + token.key})

        self.assertRaises(AuthenticationFailed, auth.authenticate, request)
