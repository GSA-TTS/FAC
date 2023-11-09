import logging

logger = logging.getLogger(__name__)


class Section:
    def __init__(self):
        self.dict_instance = {}

    def normalize_number(self, number: str):
        if number in ["N/A", "", None]:
            return "0"
        if self.is_positive(number):
            return number
        return "0"

    def is_positive(self, s):
        try:
            value = int(s)
            return value >= 0
        except ValueError:
            return False

    def get_dict(self):
        return self.dict_instance
