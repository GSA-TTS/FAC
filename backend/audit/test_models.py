from django.test import TestCase

from model_bakery import baker

from .models import Access, SingleAuditChecklist


# Create your tests here.
class SingleAuditChecklistTests(TestCase):
    def test_str_is_id_and_uei(self):
        """String representation of SAC instance is #{ID} - UEI({UEI})"""
        sac = baker.make(SingleAuditChecklist)
        self.assertEqual(str(sac), f"#{sac.id} - UEI({sac.uei})")


class AccessTests(TestCase):
    def test_str_is_id_and_uei(self):
        """
        String representation of Access instance is:

            {email} as {role} for {sac}
        """
        access = baker.make(Access)
        expected = f"{access.email} as {access.role} for {access.sac}"
        self.assertEqual(str(access), expected)
