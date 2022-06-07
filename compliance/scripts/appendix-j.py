#!/usr/bin/env python3

from trestle.oscal.catalog import Catalog
from trestle.oscal.common import Metadata

from uuid import uuid4
from datetime import datetime
import pathlib
import csv
import sys

from utils import section

# manually copied from NIST Special Publication 800-53 revision 4 PDF
# https://docs.google.com/spreadsheets/d/1XtSfqzQIaAzEuQDGcyfN6285pZyybR-eyjn5upY9EzY/edit?usp=sharing
if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} nist-800-53-rev-4-appendix-j.csv")
    sys.exit(1)
filename = sys.argv[1]

header_names = [
    "id",
    "title",
    "control",
    "guidance",
]

# Descriptions (typos and all) are copied verbatim from the official NIST 800 53
# rev4 PDF.
top_level = [
    {
        "id": "ap",
        "title": "Authority and Purpose",
        "prose": "This family ensures that organizations: (i) identify the legal bases that authorize a particular personally identifiable information (PII) collection or activity that impacts privacy; and (ii) specify in their notices the purpose(s) for which PII is collected.",
    },
    {
        "id": "ar",
        "title": "Accountability, Audit, and Risk Management",
        "prose": "This family enhances public confidence through effective controls for governance, monitoring, risk management, and assessment to demonstrate that organizations are complying with applicable privacy protection requirements and minimizing overall privacy risk.",
    },
    {
        "id": "di",
        "title": "Data Quality and Integrity",
        "prose": "This family enhances public confidence that any personally identifiable information (PII) collected and maintained by organizations is accurate, relevant, timely, and complete for the purpose for which it is to be used, as specified in public notices.",
    },
    {
        "id": "dm",
        "title": "Data Minimization and Retention",
        "prose": "This family helps organizations implement the data minimization and retention requirements to collect, use, and retain only personally identifiable information (PII) that is relevant and necessary for the purpose for which it was originally collected. Organizations retain PII for only as long as necessary to fulfill the purpose(s) specified in public notices and in accordance with a National Archives and Records Administration (NARA)-approved record retention schedule.",
    },
    {
        "id": "ip",
        "title": "Individual Participation and Redress",
        "prose": "This family addresses the need to make individuals active participants in the decision-making process regarding the collection and use of their personally identifiable information (PII). By providing individuals with access to PII and the ability to have their PII corrected or amended, as appropriate, the controls in this family enhance public confidence in organizational decisions made based on the PII.",
    },
    {
        "id": "se",
        "title": "Security",
        "prose": "This family supplements the security controls in Appendix F to ensure that technical, physical, and administrative safeguards are in place to protect personally identifiable information (PII) collected or maintained by organizations against loss, unauthorized access, or disclosure, and to ensure that planning and responses to privacy incidents comply with OMB policies and guidance. The controls in this family are implemented in coordination with information security personnel and in accordance with the existing NIST Risk Management Framework.",
    },
    {
        "id": "tr",
        "title": "Transparency",
        "prose": "This family ensures that organizations provide public notice of their information practices and the privacy impact of their programs and activities.",
    },
    {
        "id": "ul",
        "title": "Use Limitation",
        "prose": "This family ensures that organizations only use personally identifiable information (PII) either as specified in their public notices, in a manner compatible with those specified purposes, or as otherwise permitted by law. Implementation of the controls in this family will ensure that the scope of PII use is limited accordingly.",
    },
]

fd = csv.reader(open(filename, "r"))
next(fd)  # skip first line

# first pass: extract relevant values from the csv.
j = list()
headers = next(fd)
for line in fd:
    control = line[header_names.index("control")].replace("    ", "\n")
    guidance = line[header_names.index("guidance")].replace("    ", "\n")
    prose = f"{control}\n\n{guidance}"
    datum = {
        "id": line[header_names.index("id")].lower(),
        "title": line[header_names.index("title")],
        "prose": prose,
    }
    j.append(datum)

# second pass: nest control groups.
groups = []
current = []
top_ids = list(map(lambda x: x["id"], top_level))
current_toplevel = None
for control in j:
    id = control["id"]
    toplevel = id.split("-")[0]
    # are we still on the current toplevel? if we are, then continue appending
    # controls. otherwise, create a new toplevel and empty group with it.
    if toplevel != current_toplevel:
        if len(current) != 0:
            groups.append(current)
        current_toplevel = toplevel
        applicables = [level for level in top_level if level["id"] == current_toplevel]
        current = section(applicables[0])
        current["controls"] = []
    current["controls"].append(section(control))

# append the final section.
groups.append(current)

# finally, generate the catalog.
metadata = Metadata(
    title="NIST 800 53 rev 4 Appendix J",
    last_modified=datetime.now().astimezone(),
    version="0.0.1",
    oscal_version="1.0.0",
    remarks="Appendix J",
)
cid = Catalog(metadata=metadata, uuid=str(uuid4()))
cid.groups = groups
cid.oscal_write(pathlib.Path("nist-appendix-j.json"))
