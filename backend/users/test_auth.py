from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from audit.models import Access

from .auth import FACAuthenticationBackend

from model_bakery import baker
from uuid import uuid4

User = get_user_model()


class FACAuthenticationBackendTests(TestCase):
    def test_no_user_info_returns_none(self):
        """
        If user_info is empty, no user should be returned from authenticate
        """
        backend = FACAuthenticationBackend()

        factory = RequestFactory()
        request = factory.get("/")

        user = backend.authenticate(request)

        self.assertIsNone(user)

    def test_existing_user_returns_user(self):
        """
        If there is an existing user associated with the user_info, that user should be returned
        """
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
        """
        If there is no existing user associated with the user_info, a new user should be created and returned
        """
        login_id = str(uuid4())

        backend = FACAuthenticationBackend()

        factory = RequestFactory()
        request = factory.get("/")

        user_info = {"sub": login_id, "email": "a@a.com"}

        user = backend.authenticate(request, **user_info)

        self.assertEqual(user.username, login_id)
        self.assertEqual(user.email, "a@a.com")

    def test_audit_access_granted_existing_user(self):
        """
        If an existing user has unclaimed Access objects, they should be claimed during authentication
        """
        backend = FACAuthenticationBackend()

        login_id = str(uuid4())
        email = "a@a.com"

        baker.make(User, username=login_id, email=email)
        access = baker.make(Access, email=email)

        user_info = {"sub": login_id, "email": email, "all_emails": [email]}

        factory = RequestFactory()
        request = factory.get("/")

        user = backend.authenticate(request, **user_info)

        updated_access = Access.objects.get(pk=access.id)

        self.assertEqual(user, updated_access.user)

    def test_audit_access_granted_new_user(self):
        """
        If a new user has unclaimed Access objects, they should be claimed during authentication
        """
        backend = FACAuthenticationBackend()

        login_id = str(uuid4())
        email = "a@a.com"

        access = baker.make(Access, email=email)

        user_info = {"sub": login_id, "email": email, "all_emails": [email]}

        factory = RequestFactory()
        request = factory.get("/")

        user = backend.authenticate(request, **user_info)

        updated_access = Access.objects.get(pk=access.id)

        self.assertEqual(user, updated_access.user)

    def test_multiple_audit_access_granted(self):
        """
        If the user has multiple unclaimed Access objects, all of them should be claimed during authentication
        """
        backend = FACAuthenticationBackend()

        login_id = str(uuid4())
        email = "a@a.com"

        access1 = baker.make(Access, email=email)
        access2 = baker.make(Access, email=email)

        user_info = {"sub": login_id, "email": email, "all_emails": [email]}

        factory = RequestFactory()
        request = factory.get("/")

        user = backend.authenticate(request, **user_info)

        updated_access1 = Access.objects.get(pk=access1.id)
        updated_access2 = Access.objects.get(pk=access2.id)

        self.assertEqual(user, updated_access1.user)
        self.assertEqual(user, updated_access2.user)
