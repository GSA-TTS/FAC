from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIClient

from .auth import ExpiringTokenAuthentication, JWTUpsertAuthentication
from .views import AuthToken

from model_bakery import baker

User = get_user_model()

TOKEN_PATH = reverse("token")


class AuthTokenViewTests(TestCase):
    def test_authentication_classes(self):
        """
        AuthToken views should allow JWTUpsertAuthentication and ExpiringTokenAuthentication
        """
        view = AuthToken()

        # AuthToken views should allow JWTUpsertAuthentication
        self.assertIn(JWTUpsertAuthentication, view.authentication_classes)
        # AuthToken views should allow ExpiringTokenAuthentication
        self.assertIn(ExpiringTokenAuthentication, view.authentication_classes)
        # AuthToken should *only* allow the above authentication classes
        self.assertEqual(len(view.authentication_classes), 2)

        # AuthToken views should require that the user is authenticated
        self.assertIn(IsAuthenticated, view.permission_classes)
        self.assertEqual(len(view.permission_classes), 1)

    def test_no_existing_token(self):
        """
        if a user has no existing tokens, one should be created
        """
        user = baker.make(User)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(TOKEN_PATH)

        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", data)

    def test_existing_token(self):
        """
        if a user has an existing token, a new one should be created in its place
        """
        user = baker.make(User)
        token = baker.make(Token, user=user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(TOKEN_PATH)

        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", data)
        self.assertNotEqual(token.key, data["token"])

    def test_delete_token(self):
        """
        if the delete endpoint is hit, the token associated with the authenticated user should be deleted
        """
        user = baker.make(User)
        baker.make(Token, user=user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete(TOKEN_PATH)

        self.assertEqual(response.status_code, 200)

        # there should no longer be a token associated with this user
        tokens = Token.objects.filter(user=user)
        self.assertEqual(tokens.count(), 0)
