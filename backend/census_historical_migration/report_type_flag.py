import copy
from typing import Any


class AceFlag:
    """Hold ACE report flag for the ongoing report migration"""

    DEFAULT: dict[str, Any] = {
        "is_ace_report": False,
    }
    fields = copy.deepcopy(DEFAULT)

    @staticmethod
    def reset():
        AceFlag.fields = copy.deepcopy(AceFlag.DEFAULT)

    @staticmethod
    def set_ace_report_flag(flag):
        AceFlag.fields["is_ace_report"] = flag

    @staticmethod
    def get_ace_report_flag():
        return AceFlag.fields["is_ace_report"]
