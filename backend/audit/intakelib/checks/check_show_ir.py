import logging
from pprint import pprint

logger = logging.getLogger(__name__)


def show_ir(banner_text):
    def _helper(ir):
        print(f"============== BEGIN {banner_text} BEGIN ==============")
        pprint(ir)
        print(f"============== END {banner_text} END ==============")
        return ir

    return _helper
