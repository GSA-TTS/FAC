from django.test import TestCase

from model_bakery import baker

from .models import ELECAUDITHEADER


class C2FModelsTestCase(TestCase):
    def test_can_load_model(self):
        gen = ELECAUDITHEADER.objects.all()
        self.assertIsNotNone(gen)
        baker.make(ELECAUDITHEADER).save()
        gen = ELECAUDITHEADER.objects.all()
        self.assertEquals(len(gen), 1)
