import os
from audit.services.excel_validation.validate_workbook import validate_workbook
from pathlib import Path

file_path = Path("/src/audit/test/MergedWorkbook_goodLMH.xlsx")

print(f"Running validation for: {file_path}")
results = validate_workbook(file_path)

if results["errors"]:
    print("\n ERRORS:")
    for err in results["errors"]:
        print(f"- {err}")
else:
    print("\n No validation errors found.")

if results["warnings"]:
    print("\n WARNINGS:")
    for warn in results["warnings"]:
        print(f"- {warn}")
