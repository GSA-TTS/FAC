from django.test import TestCase

from model_bakery import baker

from .models import SingleAuditChecklist


# Create your tests here.
class SingleAuditChecklistTests(TestCase):

    def test_str_is_id_and_ein(self):
        """String representation of SAC instance is #{ID} - UEI({UEI})"""
        sac = baker.make(SingleAuditChecklist)
        self.assertEqual(str(sac), f'#{sac.id} - UEI({sac.uei})')
