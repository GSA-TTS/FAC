from collections import namedtuple as NT

# Types
NoMapping = NT('NoMapping', '')
MapRetype = NT('MapRetype', 'map_to retype')
MapOneOf = NT('MapOneOf', 'source dest')
MapLateRemove = NT('MapLateRemove', '')

REPORT_ID = 0


def next_report_id(year, d):
    global REPORT_ID
    REPORT_ID += 1
    month = "UNKNOWN"
    if d:
        month = d.strftime('%B')
    return f"{year}-{month}-{REPORT_ID:07}"
