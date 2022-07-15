from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from jwt import InvalidTokenError

from model_bakery import baker

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from audit.models import Access

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

    def test_no_all_emails_claim(self):
        """
        if token contains no all_emails claim, an exception should be raised
        """
        auth = JWTUpsertAuthentication()

        login_id = str(uuid4())

        token = {"sub": login_id, "email": "test-email@test.test"}

        self.assertRaises(InvalidTokenError, auth.get_user, token)

    def test_new_user(self):
        """
        if no internal user or LoginGovUser exist, new ones should be created
        """
        auth = JWTUpsertAuthentication()

        login_id = str(uuid4())

        token = {
            "sub": login_id,
            "email": "test-email@test.test",
            "all_emails": ["test-email@test.test"],
        }

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

        token = {
            "sub": login_id,
            "email": "existing-user@test.test",
            "all_emails": ["existing-user@test.test"],
        }

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

        token = {
            "sub": login_id,
            "email": existing_user.email,
            "all_emails": [existing_user.email],
        }

        user = auth.get_user(token)

        self.assertIsNotNone(user)
        self.assertEqual(user.id, existing_user.id)
        self.assertEqual(user.username, existing_user.username)
        self.assertEqual(user.email, existing_user.email)

    def test_audit_access_granted_existing_user(self):
        """
        if there are pending access invitations (Access objects w/o user_id), the user_id should be
        updated to that of the current user during the login process
        """
        existing_user = baker.make(User, email="existing-user@test.test")
        login_id = str(uuid4())

        baker.make(Access, email=existing_user.email, user_id=None)

        auth = JWTUpsertAuthentication()

        token = {
            "sub": login_id,
            "email": existing_user.email,
            "all_emails": [existing_user.email],
        }

        self.assertFalse(Access.objects.filter(user_id=existing_user).exists())

        auth.get_user(token)

        self.assertTrue(Access.objects.filter(user_id=existing_user).exists())

    def test_audit_access_granted_new_user(self):
        """
        if there are pending access invitations (Access objects w/o user_id), the user_id should be
        updated to that of the newly created user during the login process
        """
        login_id = str(uuid4())
        primary_email = "new-user@test.test"
        backup_email = "new-user-2@test.test"

        baker.make(Access, email=backup_email, user_id=None)

        auth = JWTUpsertAuthentication()

        token = {
            "sub": login_id,
            "email": primary_email,
            "all_emails": [primary_email, backup_email],
        }

        # before logging in, the access object has no associated user, just an email
        invites = Access.objects.filter(email=backup_email)
        self.assertEqual(len(invites), 1)
        self.assertIsNone(invites[0].user_id)

        auth.get_user(token)

        user = User.objects.get(email=primary_email)

        # after logging in, the access object references the newly-created user
        accesses = Access.objects.filter(email=backup_email)
        self.assertEqual(len(accesses), 1)
        self.assertEqual(accesses[0].user_id, user)

    def test_multiple_audit_access_granted(self):
        """
        if there are multiple pending access invitations (Access objects w/o user_id), the user_id of all
        should be updated to that of the current user during the login process
        """
        primary_email = "existing-user@test.test"
        backup_email_1 = "existing-user-2@test.test"
        backup_email_2 = "existing-user-3@test.test"

        existing_user = baker.make(User, email=primary_email)
        login_id = str(uuid4())

        baker.make(Access, email=backup_email_1, user_id=None)
        baker.make(Access, email=backup_email_2, user_id=None)

        auth = JWTUpsertAuthentication()

        token = {
            "sub": login_id,
            "email": existing_user.email,
            "all_emails": [primary_email, backup_email_1, backup_email_2],
        }

        self.assertFalse(Access.objects.filter(user_id=existing_user).exists())

        auth.get_user(token)

        self.assertEqual(Access.objects.filter(user_id=existing_user).count(), 2)

    def test_primary_email_change(self):
        """
        if a user changes their primary email on the LoginGov side, we should still
        find their User record using the all_emails collection
        """
        primary_email = "existing-user@test.test"
        backup_email_1 = "existing-user-2@test.test"
        backup_email_2 = "existing-user-3@test.test"

        login_id = str(uuid4())

        auth = JWTUpsertAuthentication()

        token_1 = {
            "sub": login_id,
            "email": primary_email,
            "all_emails": [primary_email, backup_email_1, backup_email_2],
        }

        user_1 = auth.get_user(token_1)

        token_2 = {
            "sub": login_id,
            "email": backup_email_1,
            "all_emails": [primary_email, backup_email_1, backup_email_2],
        }

        user_2 = auth.get_user(token_2)

        self.assertEqual(user_1, user_2)

    def test_multiple_user_records_with_primary(self):
        """
        if a user presents a LoginGov token, where the all_emails collection
        produces multiple User record matches, we should return the one that
        matches the LoginGov primary email
        """
        primary_email = "existing-user@test.test"
        backup_email_1 = "existing-user-2@test.test"
        backup_email_2 = "existing-user-3@test.test"

        existing_user_primary = baker.make(User, email=primary_email)
        baker.make(User, email=backup_email_1)

        login_id = str(uuid4())

        auth = JWTUpsertAuthentication()

        token = {
            "sub": login_id,
            "email": primary_email,
            "all_emails": [primary_email, backup_email_1, backup_email_2],
        }

        user = auth.get_user(token)

        self.assertEqual(user, existing_user_primary)

    def test_multiple_user_records_without_primary(self):
        """
        if a user presents a LoginGov token, where the all_emails collection
        produces multiple User record matches, and none of them match the LoginGov
        primary email, we should return the first match
        """
        primary_email = "existing-user@test.test"
        backup_email_1 = "existing-user-2@test.test"
        backup_email_2 = "existing-user-3@test.test"

        existing_user_backup_1 = baker.make(User, email=primary_email)
        baker.make(User, email=backup_email_1)

        login_id = str(uuid4())

        auth = JWTUpsertAuthentication()

        token = {
            "sub": login_id,
            "email": primary_email,
            "all_emails": [primary_email, backup_email_1, backup_email_2],
        }

        user = auth.get_user(token)

        self.assertEqual(user, existing_user_backup_1)

    def test_duplicate_user_email(self):
        """
        if there are multiple User records with the same email address
        an InvalidTokenError should be raised, as this is an unexpected
        scenario and is only possible if duplicate Users are created manually
        via Django admin or directly added to the database
        """
        email = "existing-user@test.test"

        baker.make(User, email=email)
        baker.make(User, email=email)

        login_id = str(uuid4())

        auth = JWTUpsertAuthentication()

        token = {
            "sub": login_id,
            "email": email,
            "all_emails": [email],
        }

        self.assertRaises(InvalidTokenError, auth.get_user, token)


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
