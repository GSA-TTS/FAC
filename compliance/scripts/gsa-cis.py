#!/usr/bin/env python3

from trestle.oscal.catalog import Catalog
from trestle.oscal.common import Metadata

from uuid import uuid4
from datetime import datetime
import pathlib
import csv
import sys

from utils import section

# the gsa docker benchmark csv needs to be downloaded manually from:
# https://docs.google.com/spreadsheets/d/15HBgrHs1hp1JWpk9FOS-5wIFwFX0QCHi0b56TX8_T5Y/edit#gid=1105465601
# (be sure to select the "GSA Docker Security Benchmark tab")
if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} gsa-docker-benchmark.csv")
    sys.exit(1)
filename = sys.argv[1]

header_names = [
    "cis_id",
    "cis_level",
    "scored",
    "docker_component",
    "in_gsa_compliance_report",
    "title",
    "parameter",
    "exception",
    "justification",
    "notes",
    # rest are ignored
]

# GSA uses CIS Docker Benchmark v1.2. These descriptions (typos and all) are
# copied verbatim from the official CIS 1.2.0 PDF.
top_level = [
    {
        "id": "1",
        "title": "General Configuration",
        "prose": "This section contains general host recommendations for systems running Docker.",
    },
    {
        "id": "2",
        "title": "Docker daemon configuration",
        "prose": "This section lists the recommendations that alter and secure the behavior of the Docker daemon. The settings that are under this section affect ALL container instances.",
    },
    {
        "id": "3",
        "title": "Docker daemon configuration files",
        "prose": "This section covers Docker related files and directory permissions and ownership. Keeping the files and directories, that may contain sensitive parameters, secure is important for correct and secure functioning of Docker daemon.",
    },
    {
        "id": "4",
        "title": "Container Images and Build File Configuration",
        "prose": "Container base images and build files govern the fundamentals of how a container instance from a particular image would behave. Ensuring that you are using proper base images and appropriatebuild files can be very important for building your containerized infrastructure. Below are some of the recommendations that you should follow for container base images and build files to ensure that your containerized infrastructure is secure.",
    },
    {
        "id": "5",
        "title": "Container Runtime Configuration",
        "prose": "There are many security implications associated with the ways that containers are started. Some runtime parameters can be supplied that have security consequences that could compromise the host and the containers running on it. It is therefore very important to verify the way in which containers are started, and which parameters are associated with them. Container runtime configuration should be reviewed in line with organizational security policy.",
    },
    {
        "id": "6",
        "title": "Docker Security Operations",
        "prose": "This section covers some of the operational security issues associated with Docker deployments. These are best practices that should be followed where possible. Most of the recommendations in this section simply act as reminders that organizations should extend their current security best practices and policies to include containers.",
    },
    {
        "id": "7",
        "title": "Docker Swarm Configuration",
        "prose": "This section lists the recommendations that alter and secure the behavior of the Docker Swarm. If you are not using Docker Swarm then the recommendations in this section do not apply.",
    },
    {
        "id": "8",
        "title": "Docker Enterprise Configuration",
        "prose": "This section contains recommendations for securing Docker Enterprise components.",
    },
]

fd = csv.reader(open(filename, "r"))
next(fd)  # skip first line

# first pass: extract relevant values from the csv.
cis = list()
headers = next(fd)
for line in fd:
    extract = line[: len(header_names)]
    # don't allow mustache markup in prose. this messes up trestle since it
    # tries to do variable substitution.
    prose = extract[header_names.index("parameter")]
    prose = prose.replace("{{", "<").replace("}}", ">")
    datum = {
        "id": extract[header_names.index("cis_id")],
        "title": extract[header_names.index("title")],
        "prose": prose,
    }
    cis.append(datum)

# the controls in the spreadsheet are not in order. this is also a buggy
# (lexographical) sorting but its good enough for our purposes.
cis.sort(key=lambda item: item["id"])

# second pass: nest control groups.
groups = []
current = []
current_toplevel = 0
for control in cis:
    id = control["id"]
    toplevel = int(id.split(".")[0])
    # are we still on the current toplevel? if we are, then continue appending
    # controls. otherwise, create a new toplevel and empty group with it.
    if toplevel != current_toplevel:
        if len(current) != 0:
            groups.append(current)
        current_toplevel = toplevel
        current = section(top_level[current_toplevel - 1])
        current["controls"] = []
    current["controls"].append(section(control, prefix="s"))

# append the final section.
groups.append(current)

# finally, generate the catalog.
metadata = Metadata(
    title="GSA Docker Security Benchmark",
    last_modified=datetime.now().astimezone(),
    version="0.0.1",
    oscal_version="1.0.0",
    remarks="This catalog is extracted from the GSA Docker Security Benchmark and may not fully comply with CIS baselines.",
)
cid = Catalog(metadata=metadata, uuid=str(uuid4()))
cid.groups = groups
cid.oscal_write(pathlib.Path("gsa-docker-security-benchmark-catalog.json"))
