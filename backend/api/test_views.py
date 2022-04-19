from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from model_bakery import baker

User = get_user_model()


class EligibilityViewTests(TestCase):
    PATH = reverse('eligibility')
    SUCCESS = {'is_usa_based': True, 'met_spending_threshold': True, 'user_provided_organization_type': 'state'}
    INELIGIBLE = {'is_usa_based': False, 'met_spending_threshold': True, 'user_provided_organization_type': 'state'}

    def test_auth_required(self):
        """Unauthenticated requests return unauthorized response"""
        client = APIClient()
        response = client.post(self.PATH, self.SUCCESS, format='json')
        self.assertEqual(response.status_code, 401)

    def test_success_and_failure(self):
        """
        An authenticated request receives an eligible response and an ineligible response
        """
        client = APIClient()
        user = baker.make(User)
        client.force_authenticate(user=user)

        response = client.post(self.PATH, self.SUCCESS, format='json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['eligible'], True)

        response = client.post(self.PATH, self.INELIGIBLE, format='json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['eligible'], False)
