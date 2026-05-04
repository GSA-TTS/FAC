import json
from openpyxl import Workbook
from django.core.management.base import BaseCommand
from dissemination.models.general import General
from dissemination.models.federalaward import FederalAward
from dissemination.models.finding import Finding
from dissemination.models.findingtext import FindingText
from dissemination.models.note import Note
from dissemination.models.captext import CapText

class Command(BaseCommand):
    help = 'Export in-progress submission data by report_id into an Excel workbook'

    def handle(self, *args, **kwargs):
        report_id = input("Enter the report ID (e.g. 2024-10-GSAFAC-0000386512): ").strip()

        wb = Workbook()
        wb.remove(wb.active)

        def add_sheet_from_queryset(title, queryset):
            sheet = wb.create_sheet(title)
            data = list(queryset.values())
            if not data:
                sheet.append(["(no records)"])
                return
            headers = sorted(data[0].keys())
            sheet.append(headers)
            for record in data:
                sheet.append([record.get(h) for h in headers])

        models = [
            ("General", General),
            ("FederalAwards", FederalAward),
            ("Findings", Finding),
            ("FindingsText", FindingText),
            ("CorrectiveActionPlan", CapText),
            ("NotesToSefa", Note),
        ]

        for title, model in models:
            qs = model.objects.filter(report_id=report_id)
            add_sheet_from_queryset(title, qs)

        output_path = f"/src/audit/exports/{report_id}_inprogress.xlsx"
        wb.save(output_path)
        self.stdout.write(self.style.SUCCESS(f"✅ Exported to: {output_path}"))
