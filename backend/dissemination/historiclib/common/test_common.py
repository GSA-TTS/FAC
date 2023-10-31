from django.test import SimpleTestCase
from .uei_to_uei import uei_to_uei
from dissemination.historiclib.exceptions import MigrationMappingError

class TestCommonMappingFunctions(SimpleTestCase):
    def test_to_uei_fail(self):
        try:
            uei_to_uei("EIEIO")
        except MigrationMappingError:
            return True
        self.assertFalse()
 
    def test_to_uei_pass(self):
        try:
            uei_to_uei("ABCDEFG")
        except MigrationMappingError:
            self.assertFalse()
        
