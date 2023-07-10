"""
Each validator added must be imported and added to the functions list below.

Each validator should be a single function in a single file.
The name of the function should match the name of the file.

Each validator function should take a dictionary as its only argument; this
dictionary has these top-level fields:

    "general_information"
    "federal_awards"
    "corrective_action_plan"
    "findings_text"
    "findings_uniform_guidance"
    "additional_ueis"

Each of those contains a list or dict representing that section.
These are already Python objects; no JSON deserialization is required.

Each validator function should return either an empty list if there are no
errors or a list of dicts where each dict has a single field, "error", that
has a string describing the error as its value.
This value is intended to be shown to the user.

So, the no-errors return value is:

    []

And an exmaple with-errors return value is:

    [{"error": "You have brought shame to your profession."}]

"""
from .auditee_ueis_match import auditee_ueis_match
from .additional_ueis import additional_ueis

functions = [
    auditee_ueis_match,
    additional_ueis,
]
