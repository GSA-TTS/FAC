import json
import re
import sys
from pathlib import Path

SCHEMAS_DIR = Path(__file__).resolve().parent.parent

VERSION_FILE = SCHEMAS_DIR / "source" / "data" / "workbook_version.json"
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


def load_workbook_version_config() -> dict:
    if not VERSION_FILE.exists():
        raise RuntimeError(f"Could not find workbook version config: {VERSION_FILE}")

    with VERSION_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_current_workbook_version() -> str:
    config = load_workbook_version_config()
    return config["current_workbook_version"]


def update_workbook_version_config(new_version: str) -> None:
    VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)

    config = load_workbook_version_config()

    authorized_versions = config.get("authorized_workbook_versions", [])

    if new_version not in authorized_versions:
        authorized_versions.append(new_version)

    config["current_workbook_version"] = new_version
    config["authorized_workbook_versions"] = authorized_versions

    VERSION_FILE.write_text(
        json.dumps(config, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Updated workbook version config to {new_version}")


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
        update_workbook_version_config(new_version)
        print("Version is already set. Updated config only.")
        return

    update_section_schema_versions(previous_version)
    update_workbook_version_config(new_version)

    print("Done!")


if __name__ == "__main__":
    main()
