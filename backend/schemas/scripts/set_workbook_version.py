import re
import sys
from pathlib import Path


SCHEMAS_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = SCHEMAS_DIR.parent

SHEETS_FILE = SCHEMAS_DIR / "source" / "excel" / "libs" / "Sheets.libsonnet"
CHECK_VERSION_FILE = (
    BACKEND_DIR / "audit" / "intakelib" / "checks" / "check_version_number.py"
)

SECTION_SCHEMA_DIR = SCHEMAS_DIR / "source" / "sections"

SECTION_SCHEMA_FILES = [
    "AdditionalEINs.schema.jsonnet",
    "AdditionalUEIs.schema.jsonnet",
    "AuditFindingsText.schema.jsonnet",
    "CorrectiveActionPlan.schema.jsonnet",
    "FederalAwards.schema.jsonnet",
    "FederalAwardsAuditFindings.schema.jsonnet",
    "NotesToSefa.schema.jsonnet",
    "SecondaryAuditors.schema.jsonnet",
]


def get_current_workbook_version() -> str:
    text = SHEETS_FILE.read_text(encoding="utf-8")
    match = re.search(
        r"local\s+WORKBOOKS_VERSION\s*=\s*['\"]([^'\"]+)['\"];",
        text,
    )

    if not match:
        raise RuntimeError("Could not find WORKBOOKS_VERSION")

    return match.group(1)


def update_sheets_version(new_version: str) -> None:
    text = SHEETS_FILE.read_text(encoding="utf-8")

    updated = re.sub(
        r"local\s+WORKBOOKS_VERSION\s*=\s*['\"][^'\"]+['\"];",
        f"local WORKBOOKS_VERSION = '{new_version}';",
        text,
        count=1,
    )

    if updated == text:
        raise RuntimeError("Could not update WORKBOOKS_VERSION")

    SHEETS_FILE.write_text(updated, encoding="utf-8")
    print(f"Updated Sheets.libsonnet to {new_version}")


def update_authorized_versions(new_version: str) -> None:
    text = CHECK_VERSION_FILE.read_text(encoding="utf-8")

    if f'"{new_version}"' in text:
        print(f"AUTHORIZED_VERSIONS already contains {new_version}")
        return

    updated = re.sub(
        r"(AUTHORIZED_VERSIONS\s*=\s*\{)",
        rf'\1\n    "{new_version}",',
        text,
        count=1,
    )

    if updated == text:
        raise RuntimeError("Could not update AUTHORIZED_VERSIONS")

    CHECK_VERSION_FILE.write_text(updated, encoding="utf-8")
    print(f"Added {new_version} to AUTHORIZED_VERSIONS")


def update_section_schema_versions(previous_version: str) -> None:
    for filename in SECTION_SCHEMA_FILES:
        path = SECTION_SCHEMA_DIR / filename
        text = path.read_text(encoding="utf-8")

        if f"'{previous_version}'" in text:
            print(f"{filename}: already contains {previous_version}")
            continue

        updated = text.replace(
            "Sheets.WORKBOOKS_VERSION,",
            f"'{previous_version}',\n        Sheets.WORKBOOKS_VERSION,",
            1,
        )

        if updated == text:
            raise RuntimeError(f"Could not update version enum in {filename}")

        path.write_text(updated, encoding="utf-8")
        print(f"{filename}: added {previous_version}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/set_workbook_version.py <version>")

    new_version = sys.argv[1]

    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        raise SystemExit(f"Invalid version format: {new_version}")

    previous_version = get_current_workbook_version()

    print(f"Previous version: {previous_version}")
    print(f"New version: {new_version}")

    if previous_version == new_version:
        print("Version is already set. No version bump needed.")
        return

    update_section_schema_versions(previous_version)
    update_sheets_version(new_version)
    update_authorized_versions(new_version)

    print("Done!")


if __name__ == "__main__":
    main()
    