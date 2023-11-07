import logging

logger = logging.getLogger(__name__)


class Section:
    def __init__(self):
        self.dict_instance = {}

    def get_dict(self):
        return self.dict_instance
