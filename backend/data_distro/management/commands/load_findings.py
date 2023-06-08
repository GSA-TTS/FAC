import logging
from typing import Any, Optional

from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
from psycopg2._psycopg import connection
from psycopg2 import ProgrammingError

from data_distro.models import FindingText, Finding

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("report_id", type=str)

    def handle(self, *args, **options: Any) -> str | None:
        """ Fetch the relevant values of the Finding with report_id from 
        23 data and create an instance of the Finding model from it."""
        environments = ["DEVELOPMENT", "STAGING", "PRODUCTION"]
        if settings.ENVIRONMENT not in environments:
            connection_string = (
                "dbname='postgres' user='postgres' port=5432, "
                "host='db'"
            )
        else:
            connection_string = settings.CONNECTION_STRING
        report_id = options["report_id"]
        sql = (
            "select findings_text, general_information, "
            "findings_uniform_guidance from "
            "audit_singleauditchecklist where report_id" 
            f"= '{report_id}';"
        )
        connection_ = connection(connection_string)
        connection_.autocommit = True
        with connection_.cursor() as cursor:
            cursor.execute(sql)
            query_results = cursor.fetchone()

        # query_results will be a Tuple.  The first element will
        # be findings_text, the second will be general_information,
        # and third will be the findings_uniform_guidance.
        findings_text_dict = query_results[0]
        general_information_dict = query_results[1]
        findings_uniform_guidance = query_results[2]
        self.stdout.write(str(findings_uniform_guidance))

        # Save FindingText objects first.
        # We don't currently have a mapping for sequence_number.
        sequence_number = None
        dbkey = report_id
        audit_date = general_information_dict["auditee_fiscal_period_start"]
        audit_year = audit_date.split("-")[0]
        # is_public is True by default ... for now
        is_public = True
        findings_text_entries = findings_text_dict["FindingsText"]["findings_text_entries"]
        finding_texts = []
        for entry in findings_text_entries:
            charts_tables = entry["contains_chart_or_table"] == "Y"
            finding_ref_number = entry["reference_number"]    
            text = entry["text_of_finding"]
            #Create the new FindingsText object
            finding_text = FindingText(
                charts_tables = charts_tables,
                finding_ref_number = finding_ref_number,
                sequence_number = sequence_number,
                text = text,
                dbkey = dbkey,
                audit_year = audit_year,
                is_public = is_public
            )
            finding_text.save()
            finding_texts.append(finding_text)

        # Save Finding objects.
        findings_uniform_guidance_entries = (
            findings_uniform_guidance
                ["FindingsUniformGuidance"]
                ["findings_uniform_guidance_entries"]
        )
        audit_id = 1
        for entry in findings_uniform_guidance_entries:
            findings = entry["findings"]
            # findings_text: questions around how this works
            # I suspect that this finding_ref_number should be the same
            # as the finding_ref_number for the FindingText
            finding_ref_number = findings["reference_number"]
            finding = Finding(
                # audit_id can't be null, make up a value for now
                audit_id = audit_id,
                # audit_findings_id cannot be null, make up a value
                # for now
                audit_findings_id = audit_id * 2,
                prior_finding_ref_numbers = findings.get(
                    "prior_references"
                ),
                modified_opinion = entry["modified_opinion"] == "Y",
                other_non_compliance = entry["other_matters"] == "Y",
                material_weakness = entry["material_weakness"] == "Y",
                significant_deficiency = (
                    entry["significant_deficiency"] == "Y"
                ),
                other_findings = entry["other_findings"] == "Y",
                questioned_costs = entry["questioned_costs"] == "Y",
                repeat_finding = (
                    findings["repeat_prior_reference"] == "Y"
                ),
                type_requirement = (
                    entry["program"]["compliance_requirement"]
                ),
                is_public = is_public
            )
            finding.save()
            for finding_text in finding_texts:
                finding.findings_text.add(finding_text)
            finding.save()
            audit_id += 1
