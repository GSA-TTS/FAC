from audit.models import SingleAuditChecklist
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

User = get_user_model()

ELIGIBILITY_PATH = reverse('eligibility')


class EligibilityViewTests(TestCase):
    SUCCESS = {'is_usa_based': True, 'met_spending_threshold': True, 'user_provided_organization_type': 'state'}
    INELIGIBLE = {'is_usa_based': False, 'met_spending_threshold': True, 'user_provided_organization_type': 'state'}

    def test_auth_required(self):
        """Unauthenticated requests return unauthorized response"""
        client = APIClient()
        response = client.post(ELIGIBILITY_PATH, self.SUCCESS, format='json')
        self.assertEqual(response.status_code, 401)

    def test_success_and_failure(self):
        """
        An authenticated request receives an eligible response and an ineligible response
        """
        client = APIClient()
        user = baker.make(User)
        client.force_authenticate(user=user)

        response = client.post(ELIGIBILITY_PATH, self.SUCCESS, format='json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['eligible'], True)

        response = client.post(ELIGIBILITY_PATH, self.INELIGIBLE, format='json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['eligible'], False)


class UEIValidationViewTests(TestCase):
    PATH = reverse('uei-validation')
    SUCCESS = {'uei': 'ABC123DEF456'}
    INELIGIBLE = {'uei': '000000000OI*'}

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
        self.assertEqual(data['valid'], True)

        response = client.post(self.PATH, self.INELIGIBLE, format='json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['valid'], False)


class SACCreationTests(TestCase):

    def setUp(self):
        self.user = baker.make(User)
        self.client = APIClient()

    def test_valid_data_across_steps_creates_an_sac(self):
        """Upon submitting valid data and following `next` responses, a new SAC is created """
        self.client.force_authenticate(user=self.user)

        # Submit eligibility data
        eligibility_info = {'is_usa_based': True, 'met_spending_threshold': True, 'user_provided_organization_type': 'state'}
        response = self.client.post(ELIGIBILITY_PATH, eligibility_info, format='json')
        data = response.json()
        next_step = data['next']

        # Submit auditee info
        auditee_info = {"uei": "NotARealUEI3", "auditee_fiscal_period_start": "2021-01-01", "auditee_fiscal_period_end": "2022-01-01", "auditee_name": "Tester"}
        response = self.client.post(next_step, auditee_info, format='json')
        data = response.json()
        next_step = data['next']

        # Submit Access details
        access_data = [{"role": "auditee_contact", "email": "test@example.com"}, {"role": "auditor_contact", "email": "testerc@example.com"}]
        response = self.client.post(next_step, access_data, format='json')
        data = response.json()
        sac = SingleAuditChecklist.objects.get(id=data['sac_id'])
        self.assertEqual(sac.submitted_by, self.user)
        self.assertEqual(sac.uei, "NotARealUEI3")


