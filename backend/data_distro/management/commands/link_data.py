"""Functions that the public data loader uses to build relationships between models """
import traceback

from data_distro import models as mods
from data_distro.management.commands.handle_errors import handle_exceptions


def link_objects_findings(objects_dict):
    """Adds relationships between finding and finding text"""
    if objects_dict is not None and "Finding" in objects_dict:
        findings_instance = objects_dict["Finding"]
        finding_ref_nums = findings_instance.finding_ref_number
        dbkey = str(findings_instance.dbkey)
        audit_year = findings_instance.audit_year

        # findings text to finding
        findings_text = mods.FindingText.objects.filter(
            dbkey=dbkey,
            audit_year=audit_year,
            finding_ref_number=finding_ref_nums,
        )
        for finding_text in findings_text:
            findings_instance.findings_text.add(finding_text)
            findings_instance.save()

        # finding to award
        awards_instance = mods.FederalAward.objects.get(
            dbkey=dbkey,
            audit_year=audit_year,
            audit_id=findings_instance.audit_id,
        )
        awards_instance.findings.add(findings_instance)
        awards_instance.save()

        # finding to general is taken care of in general processing


def link_objects_cpas(objects_dict, row):
    """Adds relationships between the general table and auditors for the cpas table"""
    auditor_instance = objects_dict["Auditor"]
    dbkey = row["DBKEY"]
    audit_year = row["AUDITYEAR"]
    gen_instance = mods.General.objects.get(dbkey=dbkey, audit_year=audit_year)
    gen_instance.secondary_auditors.add(auditor_instance)
    gen_instance.save()


def link_objects_general(objects_dict):
    """Adds relationships between the General model and other models"""
    # General model instance
    instance = objects_dict["General"]
    dbkey = instance.dbkey
    audit_year = instance.audit_year

    # Models that link to general

    auditee = objects_dict["Auditee"]
    instance.auditee = auditee

    auditor = objects_dict["Auditor"]
    instance.primary_auditor = auditor

    fed_awards = mods.FederalAward.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for award in fed_awards:
        instance.federal_awards.add(award)

    findings = mods.Finding.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for finding in findings:
        instance.findings.add(finding)

    findings_text = mods.FindingText.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for finding_text in findings_text:
        instance.findings_text.add(finding_text)

    cap_texts = mods.CapText.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for cap_text in cap_texts:
        instance.cap_text.add(cap_text)

    notes = mods.Note.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for note in notes:
        instance.notes.add(note)

    revisions = mods.Revision.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for revision in revisions:
        instance.revision = revision

    passthroughs = mods.Passthrough.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for passthrough in passthroughs:
        instance.passthrough.add(passthrough)

    instance.save()


def link_lists(csv_dict, payload_name):
    """
    These were their own data model but we are going to use an array field.
    This adds the fields in the right order. It should run after general.
    """
    for row in csv_dict:
        try:
            dbkey = row["DBKEY"]
            audit_year = row["AUDITYEAR"]
            payload = row[payload_name]
            general_instance = mods.General.objects.filter(
                dbkey=dbkey, audit_year=audit_year
            )[0]
            auditee_instance = general_instance.auditee

            if payload_name == "DUNS":
                existing_list = auditee_instance.duns_list
                if payload not in existing_list:
                    existing_list.append(int(payload))
                    auditee_instance.duns_list = existing_list
                    auditee_instance.save()
            elif payload_name == "UEI":
                existing_list = auditee_instance.uei_list
                if payload not in existing_list:
                    existing_list.append(str(payload))
                    auditee_instance.uei_list = existing_list
                    auditee_instance.save()
            else:
                existing_list = auditee_instance.ein_list
                if payload not in existing_list:
                    existing_list.append(int(payload))
                    auditee_instance.ein_list = existing_list
                    auditee_instance.save()
        except Exception:
            handle_exceptions(
                str(payload_name),
                None,
                str(row),
                traceback.format_exc(),
            )


def link_agency(csv_dict, file_name):
    """
    The agency table populates FederalAward agency_prior_findings_list.
    """
    for row in csv_dict:
        try:
            dbkey = row["DBKEY"]
            audit_year = row["AUDITYEAR"]
            agency = row["AGENCY"]
            ein = row["EIN"]

            # I am not sure if only one or multiples can be returned
            award_instances = mods.FederalAward.objects.filter(
                dbkey=dbkey,
                audit_year=audit_year,
                cpa_ein=ein,
            )

            for award_instance in award_instances:
                agency_list = award_instance.agency_prior_findings_list

                # 00 had been representing none, we can just use an empty list instead
                if agency_list is None:
                    award_instance.agency_prior_findings_list = []
                    agency_list = []

                if agency not in agency_list and agency != "00":
                    agency_list.append(agency)
                    award_instance.agency_prior_findings_list = agency_list
                    award_instance.save()

        except Exception:
            handle_exceptions(
                "agency",
                None,
                str(row),
                traceback.format_exc(),
            )
