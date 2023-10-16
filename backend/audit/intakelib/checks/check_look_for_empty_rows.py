from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import ranges_to_rows, appears_empty

from .util import get_range_start_row

logger = logging.getLogger(__name__)


def look_for_empty_rows(ir):
    for sheet in ir:
        if sheet["name"] in ["Form"]:
            rows = ranges_to_rows(sheet["ranges"])
            row_ndx = 0
            for row in rows:
                is_all = all(list(map(lambda v: appears_empty(v), row)))
                if is_all:
                    raise ValidationError(
                        (
                            "Row ",
                            int(get_range_start_row(sheet["ranges"][0])) + row_ndx,
                            "Empty row",
                            {
                                "text": "Remove empty rows in the middle of your data",
                                "link": "Intake checks: no link defined",
                            },
                        )
                    )
                row_ndx += 1
