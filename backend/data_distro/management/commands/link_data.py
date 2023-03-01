"""Functions that the public data loader uses to build relationships between models """
from pandas import read_csv
from data_distro import models as mods


def link_objects_findings(objects_dict):
    """Adds relationships between finding and finding text"""
    if objects_dict is not None and "Findings" in objects_dict:
        instance = objects_dict["Findings"]
        dbkey = instance.dbkey
        audit_year = instance.audit_year
        findings_text = mods.FindingsText.objects.filter(
            dbkey=dbkey, audit_year=audit_year
        )
        for finding_text in findings_text:
            instance.findings_text = finding_text
            instance.save()


def link_objects_cpas(objects_dict, row):
    """Adds relationships between the general table and auditors for the cpas table"""
    auditor_instance = objects_dict["Auditor"]
    dbkey = row["DBKEY"]
    audit_year = row["AUDITYEAR"]
    gen_instance = mods.General.objects.filter(dbkey=dbkey, audit_year=audit_year)[0]
    gen_instance.auditor.add(auditor_instance)
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

    # There can be multiple but only one from the gen form, cpas run next
    auditors = mods.Auditor.objects.filter(id=objects_dict["Auditor"].id)
    instance.auditor.set(auditors)

    cfdas = mods.CfdaInfo.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for cfda in cfdas:
        instance.cfda = cfda

    findings = mods.Findings.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for finding in findings:
        instance.findings = finding

    cap_texts = mods.CapText.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for cap_text in cap_texts:
        instance.cap_text = cap_text

    notes = mods.Notes.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for note in notes:
        instance.notes = note

    revisions = mods.Revisions.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for revision in revisions:
        instance.revidions = revision

    passthroughs = mods.Passthrough.objects.filter(dbkey=dbkey, audit_year=audit_year)
    for passthrough in passthroughs:
        instance.passthrough = passthrough

    instance.save()


def add_duns_eins(file):
    """
    These were their own data model but we are going to use an array field.
    This adds the fields in the right order. It should run after general.
    """
    file_path = f"data_distro/data_to_load/{file}"
    if "duns" in file:
        sort_by = "DUNSEQNUM"
        payload_name = "DUNS"
    else:
        sort_by = "EINSEQNUM"
        payload_name = "EIN"

    # Can't do chunks because we want to order the dataframe
    data_frame = read_csv(file_path, sep="|", encoding="mac-roman")
    # This will make sure we load the lists in the right order
    data_frame = data_frame.sort_values(by=sort_by, na_position="first")
    csv_dict = data_frame.to_dict(orient="records")

    for row in csv_dict:
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
                print(existing_list)
                auditee_instance.duns_list = existing_list
                auditee_instance.save()
        else:
            existing_list = auditee_instance.ein_list
            if payload not in existing_list:
                existing_list.append(int(payload))
                auditee_instance.ein_list = existing_list
                auditee_instance.save()


def add_agency(file_name):
    """
    De-duping agency and adding as relationships
    """
    file_path = f"data_distro/data_to_load/{file_name}"
    data_frame = read_csv(file_path, sep="|", encoding="mac-roman")
    csv_dict = data_frame.to_dict(orient="records")

    for row in csv_dict:
        dbkey = row["DBKEY"]
        audit_year = row["AUDITYEAR"]
        agency = row["AGENCY"]

        agency_instance = mods.Agencies.objects.get_or_create(
            agency_cfda=agency, is_public=True
        )[0]

        general_instance = mods.General.objects.filter(
            dbkey=dbkey, audit_year=audit_year
        )[0]
        general_instance.agency.add(agency_instance)

        auditee_instance = general_instance.auditee
        auditee_instance.agency.add(agency_instance)
        auditee_instance.save()
