from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .auth import FACAuthenticationBackend

from model_bakery import baker
from uuid import uuid4

User = get_user_model()


class FACAuthenticationBackendTests(TestCase):
    def test_no_user_info_returns_none(self):
        backend = FACAuthenticationBackend()

        factory = RequestFactory()
        request = factory.get("/")

        user = backend.authenticate(request)

        self.assertIsNone(user)

    def test_existing_user_returns_user(self):
        login_id = str(uuid4())
        existing_user = baker.make(User, username=login_id, email="a@a.com")

        backend = FACAuthenticationBackend()

        factory = RequestFactory()
        request = factory.get("/")

        user_info = {"sub": login_id, "email": existing_user.email}

        user = backend.authenticate(request, **user_info)

        self.assertEqual(user.username, existing_user.username)
        self.assertEqual(user.email, existing_user.email)

    def test_new_user_returns_user(self):
        login_id = str(uuid4())

        backend = FACAuthenticationBackend()

        factory = RequestFactory()
        request = factory.get("/")

        user_info = {"sub": login_id, "email": "a@a.com"}

        user = backend.authenticate(request, **user_info)

        self.assertEqual(user.username, login_id)
        self.assertEqual(user.email, "a@a.com")
