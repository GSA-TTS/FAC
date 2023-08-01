from collections import namedtuple as NT

######################################################
# PARSING SUPPORT
##
# This code takes the Jsonnet -> JSON object representation
# into a tree of NamedTuples. As a result, we end
# up with a "typed" tree of objects we can process/walk
# for generating the XLSX doc.
##
# It's more robust than reaching into the JSON object.
# Ideally, the parsing process would do a bit more
# checking for values; at least NT creation fails
# if we don't have the right number of fields, etc.

Sheet = NT(
    "Sheet",
    "name single_cells meta_cells open_ranges mergeable_cells merged_unreachable header_inclusion text_ranges header_height hide_col_from hide_row_from",
)
Posn = NT(
    "Posn",
    "title title_cell range_name range_cell width keep_locked format last_range_cell",
)
SingleCell = NT("SingleCell", "posn validation formula help")
# TODO: flesh out NT for meta cells
MetaCell = NT("MetaCell", "posn formula help")
MergeableCell = NT("MergeableCell", "start_row end_row start_column end_column")
MergedUnreachable = NT("MergedUnreachable", "columns")
HeaderInclusion = NT("HeaderInclusion", "cells")
Help = NT("Help", "text link")
OpenRange = NT("OpenRange", "posn validation formula help")
TextRange = NT("TextRange", "posn validation contents")
Enum = NT("Enum", "description values")
Validation = NT(
    "Validation",
    "type allow_blank operator formula1 lookup_range custom_error custom_title",
)
WB = NT("WB", "filename sheets title_row")


def parse_help(spec):
    return Help(spec["text"], spec["link"])


def get(obj, key, default=None):
    # This first condition essentially adds values into
    # the NT if they are missing in the object, and it inserts
    # them in as the default value.
    # print(f"Asking for {key} in {str(obj)[0:30]}...")
    if obj is None:
        # print("\tget returning obj was none; default")
        return default
    elif key in obj:
        # print(f"\tget returning key in obj")
        return obj[key]
    else:
        # print("\tget returning default")
        return default


def parse_validation(spec):
    return Validation(
        get(spec, "type"),
        get(spec, "allow_blank"),
        get(spec, "operator"),
        get(spec, "formula1"),
        get(spec, "lookup_range"),
        get(spec, "custom_error"),
        get(spec, "custom_title"),
    )


def parse_single_cell(spec):
    return SingleCell(
        Posn(
            get(spec, "title"),
            get(spec, "title_cell"),
            get(spec, "range_name"),
            get(spec, "range_cell"),
            get(spec, "width"),
            get(spec, "keep_locked", default=False),
            get(spec, "format", default=None),
            get(spec, "last_range_cell", default=None),
        ),
        parse_validation(get(spec, "validation")),
        get(spec, "formula"),
        parse_help(get(spec, "help")),
    )


# Meta cells probably don't need named ranges
def parse_meta_cell(spec):
    return MetaCell(
        Posn(
            get(spec, "title"),
            get(spec, "title_cell"),
            get(spec, "range_name"),
            get(spec, "range_cell"),
            get(spec, "width"),
            get(spec, "keep_locked", default=True),
            get(spec, "format", default=None),
            get(spec, "last_range_cell", default=None),
        ),
        get(spec, "formula"),
        parse_help(get(spec, "help")),
    )


def parse_open_range(spec):
    # print("------------------- open range")
    # print(f"len opr: {len(spec)}")
    return OpenRange(
        Posn(
            get(spec, "title"),
            get(spec, "title_cell"),
            get(spec, "range_name"),
            get(spec, "range_cell"),
            get(spec, "width"),
            get(spec, "keep_locked", default=False),
            get(spec, "format", default=None),
            get(spec, "last_range_cell", default=None),
        ),
        parse_validation(get(spec, "validation")),
        get(spec, "formula"),
        parse_help(get(spec, "help")),
    )


def parse_mergeable_cell(spec):
    return MergeableCell(spec[0], spec[1], spec[2], spec[3])


def parse_merged_unreachable(spec):
    # Should just be a list of columns
    if spec is None:
        return None
    return MergedUnreachable(spec)


def parse_header_inclusion(spec):
    return HeaderInclusion(spec)


def parse_text_range(spec):
    return TextRange(
        Posn(
            get(spec, "title"),
            get(spec, "title_cell"),
            get(spec, "range_name"),
            get(spec, "range_cell"),
            get(spec, "width"),
            get(spec, "keep_locked", default=False),
            get(spec, "format", default=None),
            get(spec, "last_range_cell", default=None),
        ),
        parse_validation(get(spec, "validation")),
        Enum(
            get(get(spec, "contents"), "description"),
            get(get(spec, "contents"), "enum"),
        ),
    )


def parse_sheet(spec):
    sc, mtc, opr, mc, mur, hi, tr = None, None, None, None, None, None, None
    name = get(spec, "name", default="Unnamed Sheet")
    if "single_cells" in spec:
        sc = list(map(parse_single_cell, get(spec, "single_cells", default=[])))
    else:
        sc = []
    if "meta_cells" in spec:
        mtc = list(map(parse_meta_cell, get(spec, "meta_cells", default=[])))
    else:
        sc = []
    if "open_ranges" in spec:
        opr = list(map(parse_open_range, get(spec, "open_ranges", default=[])))
    else:
        opr = []
    if "mergeable_cells" in spec:
        mc = list(map(parse_mergeable_cell, get(spec, "mergeable_cells", default=[])))
    else:
        mc = []
    if "merged_unreachable" in spec:
        mur = parse_merged_unreachable(get(spec, "merged_unreachable", default=None))
    else:
        mur = []
    if "header_inclusion" in spec:
        hi = parse_header_inclusion(get(spec, "header_inclusion"))
    else:
        hi = HeaderInclusion([])
    if "text_ranges" in spec:
        tr = list(map(parse_text_range, get(spec, "text_ranges", default=[])))
    else:
        tr = []
    if "header_height" in spec:
        hh = get(spec, "header_height")
    else:
        hh = None
    if "hide_col_from" in spec:
        hcf = get(spec, "hide_col_from")
    else:
        hcf = None
    if "hide_row_from" in spec:
        hrf = get(spec, "hide_row_from")
    else:
        hrf = None
    return Sheet(name, sc, mtc, opr, mc, mur, hi, tr, hh, hcf, hrf)


def parse_spec(spec):
    if "filename" in spec:
        return WB(
            get(spec, "filename"),
            list(map(parse_sheet, get(spec, "sheets"))),
            get(spec, "title_row"),
        )
    else:
        print("unhandled")
        print(spec)
