from django.test import TestCase
from .models import CensusGen


class C2FModelsTestCase(TestCase):
    def test_can_load_model(self):
        gen = CensusGen.objects.all()
        self.assertIsNotNone(gen)
