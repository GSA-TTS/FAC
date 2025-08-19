from typing import Any, Dict, Iterable, Mapping, Optional, Union
from collections.abc import MutableMapping

Row = Union[object, Mapping[str, Any]]


def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _normalize_status(val: Optional[str]) -> Optional[str]:
    if val is None:
        return None

    status = str(val).strip().upper()

    # Normalize known variants to canonical forms
    if status in (
        "DEPRECATED_VIA_RESUBMISSION",
        "DEPRECATED_SUBMISSION",
        "OLD_VERSION",
    ):
        return "DEPRECATED"

    if status in ("MOST_RECENT_SUBMISSION", "MOSTRECENT"):
        return "MOST_RECENT"

    return status


def _resolve_report_id(row: Row) -> Any:
    for k in ("report_id", "report_id_id", "id", "reportid", "reportID"):
        val = _get(row, k, None)
        if val is not None:
            return val
    return None


def _tag_from_resubmission_fields(row: Row) -> Optional[str]:
    status = _normalize_status(_get(row, "resubmission_status"))
    print(f"STATUS RAW: {_get(row, 'resubmission_status')} | NORMALIZED: {status}")

    if status == "MOST_RECENT":
        return "Most Recent"
    elif status == "DEPRECATED":
        return "Resubmitted"

    # Do not tag if status is missing or unknown
    return None


def build_resub_tag_map(rows: Iterable[Row]) -> Dict[Any, Optional[str]]:
    """
    Builds a mapping of report_id → tag using already-loaded data from general search results.
    """
    tag_map: Dict[Any, Optional[str]] = {}

    for row in rows:
        report_id = _resolve_report_id(row)
        if report_id is None:
            continue
        tag = _tag_from_resubmission_fields(row)
        if tag is not None:
            tag_map[report_id] = tag

    return tag_map


def attach_resubmission_tags(
    rows: Iterable[Row], tag_map: Mapping[Any, Optional[str]]
) -> None:
    """
    Injects .resubmission_tag or ['resubmission_tag'] into each row based on the tag_map.
    """
    for row in rows:
        report_id = _resolve_report_id(row)
        tag = tag_map.get(report_id)
        if isinstance(row, MutableMapping):
            row["resubmission_tag"] = tag
        else:
            setattr(row, "resubmission_tag", tag)
