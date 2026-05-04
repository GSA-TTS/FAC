import json
from openpyxl import Workbook
from django.core.management.base import BaseCommand
from audit.models import SingleAuditChecklist

class Command(BaseCommand):
    help = 'Export a SAC submission to Excel by report_id'

    def handle(self, *args, **kwargs):
        report_id = input("Enter the report ID (e.g. 2024‑10‑GSAFAC‑0000386512): ").strip()

        try:
            sac: SingleAuditChecklist = SingleAuditChecklist.objects.get(report_id=report_id)
        except SingleAuditChecklist.DoesNotExist:
            self.stderr.write("Submission not found.")
            return

        wb = Workbook()
        wb.remove(wb.active)

        sections = {
            "general_information": sac.general_information,
            "audit_information": sac.audit_information,
            "federal_awards": sac.federal_awards,
            "findings_text": sac.findings_text,
            "findings_uniform_guidance": sac.findings_uniform_guidance,
            "corrective_action_plan": sac.corrective_action_plan,
            "notes_to_sefa": sac.notes_to_sefa,
        }

        def write_json_section_to_sheet(title: str, data):
            sheet = wb.create_sheet(title)
            if isinstance(data, dict):
                for k, v in data.items():
                    sheet.append([k, json.dumps(v)])
            elif isinstance(data, list):
                if not data:
                    sheet.append(["(empty)"])
                    return
                headers = sorted(set().union(*[row.keys() for row in data]))
                sheet.append(headers)
                for row in data:
                    sheet.append([row.get(h) for h in headers])
            else:
                sheet.append([json.dumps(data)])

        for title, data in sections.items():
            write_json_section_to_sheet(title, data)

        output_file = f"/src/audit/exports/{report_id}.xlsx"
        wb.save(output_file)
        self.stdout.write(self.style.SUCCESS(f"✅ Exported to: {output_file}"))
