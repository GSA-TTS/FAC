from django.db import models

# data distro naming can go away


class DataDistroAgencies(models.Model):
    auditid = models.ForeignKey(
        "DataDistroAudits", models.DO_NOTHING, db_column="auditid"
    )
    # may want to update this to be a SmallIntegerField
    # agencies, AGENCYCFDA
    agency_cfda = models.TextField(
        "2-digit prefix of Federal Agency requiring copy of audit report",
        blank=True,
        null=True,
    )
    prior_agency = models.TextField(blank=True, null=True)
    prior_finding = models.BooleanField(blank=True, null=True)
    current_finding = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_agencies"


# would it be simpler to move this to the audit
class DataDistroAuditAuditors(models.Model):
    # general, DBKEY?
    auditid = models.ForeignKey(
        "DataDistroAudits", models.DO_NOTHING, db_column="auditid"
    )
    auditorid = models.ForeignKey(
        "DataDistroAuditors", models.DO_NOTHING, db_column="auditorid"
    )
    is_primary = models.BooleanField()

    class Meta:
        managed = False
        db_table = "data_distro_audit_auditors"


class DataDistroAuditComponents(models.Model):
    auditid = models.ForeignKey(
        "DataDistroAudits", models.DO_NOTHING, db_column="auditid"
    )
    cap = models.TextField("Corrective action plan", blank=True, null=True)
    financial_statements = models.TextField(blank=True, null=True)
    sefa = models.TextField(blank=True, null=True)
    schedule_prior_audit_findings = models.TextField(blank=True, null=True)
    opinion_on_financial_statements = models.TextField(blank=True, null=True)
    report_internal_control = models.TextField(blank=True, null=True)
    gasreport_on_compliance = models.TextField(blank=True, null=True)
    sfqc = models.TextField(blank=True, null=True)
    opinion_or_disclaimer_sfa = models.TextField(blank=True, null=True)
    gasreport_internal_control = models.TextField(blank=True, null=True)
    report_on_compliance = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_audit_components"


class DataDistroAuditDuns(models.Model):
    auditid = models.ForeignKey(
        "DataDistroAudits", models.DO_NOTHING, db_column="auditid"
    )
    dunid = models.ForeignKey("DataDistroDuns", models.DO_NOTHING, db_column="dunid")
    is_primary = models.BooleanField()

    class Meta:
        managed = False
        db_table = "data_distro_audit_duns"


class DataDistroAuditEins(models.Model):
    auditid = models.ForeignKey(
        "DataDistroAudits", models.DO_NOTHING, db_column="auditid"
    )
    einid = models.ForeignKey("DataDistroEins", models.DO_NOTHING, db_column="einid")
    is_primary = models.BooleanField()

    class Meta:
        managed = False
        db_table = "data_distro_audit_eins"


class DataDistroAuditIndicators(models.Model):
    auditid = models.ForeignKey(
        "DataDistroAudits", models.DO_NOTHING, db_column="auditid"
    )
    type_report_financial_statements = models.TextField(blank=True, null=True)
    special_framework = models.TextField(blank=True, null=True)
    special_framework_required = models.BooleanField(blank=True, null=True)
    typereport_special_framework = models.TextField(blank=True, null=True)
    going_concern = models.BooleanField(blank=True, null=True)
    material_weakness = models.BooleanField(blank=True, null=True)
    material_non_compliance = models.BooleanField(blank=True, null=True)
    type_report_major_program = models.TextField(blank=True, null=True)
    lowrisk = models.BooleanField(blank=True, null=True)
    material_weakness_major_program = models.BooleanField(blank=True, null=True)
    qcosts = models.BooleanField(blank=True, null=True)
    reportable_condition = models.BooleanField(blank=True, null=True)
    reportable_condition_major_program = models.BooleanField(blank=True, null=True)
    significant_deficiency = models.BooleanField(blank=True, null=True)
    significant_deficiency_material_weakness = models.BooleanField(
        blank=True, null=True
    )
    significant_deficiency_major_program = models.BooleanField(blank=True, null=True)
    cyfindings = models.BooleanField(blank=True, null=True)
    pyschedule = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_audit_indicators"


class DataDistroAuditRevisions(models.Model):
    auditid = models.ForeignKey(
        "DataDistroAudits", models.DO_NOTHING, db_column="auditid"
    )
    general_info = models.TextField(blank=True, null=True)
    general_info_explain = models.TextField(blank=True, null=True)
    federal_awards = models.TextField(blank=True, null=True)
    federal_awards_explain = models.TextField(blank=True, null=True)
    findings = models.TextField(blank=True, null=True)
    findings_explain = models.TextField(blank=True, null=True)
    findings_text = models.TextField(blank=True, null=True)
    findings_text_explain = models.TextField(blank=True, null=True)
    audit_info = models.TextField(blank=True, null=True)
    audit_info_explain = models.TextField(blank=True, null=True)
    cap = models.TextField(blank=True, null=True)
    cap_explain = models.TextField(blank=True, null=True)
    notes_to_sefa = models.TextField(blank=True, null=True)
    notes_to_sefa_explain = models.TextField(blank=True, null=True)
    other = models.TextField(blank=True, null=True)
    other_explain = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_audit_revisions"


class DataDistroAuditStatus(models.Model):
    auditid = models.ForeignKey(
        "DataDistroAudits", models.DO_NOTHING, db_column="auditid"
    )
    final = models.BooleanField(blank=True, null=True)
    audit_uploaded = models.BooleanField(blank=True, null=True)
    audit_upload_date = models.DateTimeField(blank=True, null=True)
    auditee_submitted = models.BooleanField(blank=True, null=True)
    auditee_submit_date = models.DateTimeField(blank=True, null=True)
    auditor_submitted = models.BooleanField(blank=True, null=True)
    auditor_submit_date = models.DateTimeField(blank=True, null=True)
    fac_submit = models.BooleanField(blank=True, null=True)
    fac_submit_date = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    submitted = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_audit_status"


class DataDistroAuditees(models.Model):
    name = models.TextField(blank=True, null=True)
    street1 = models.TextField(blank=True, null=True)
    street2 = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    contact = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    fax = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_auditees"


class DataDistroAuditors(models.Model):
    seqnum = models.SmallIntegerField(blank=True, null=True)
    firmname = models.TextField()
    ein = models.TextField(blank=True, null=True)
    street1 = models.TextField(blank=True, null=True)
    street2 = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    contact = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    fax = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_auditors"


class DataDistroAudits(models.Model):
    auditid = models.AutoField(primary_key=True)
    auditeeid = models.ForeignKey(
        DataDistroAuditees, models.DO_NOTHING, db_column="auditeeid"
    )
    audit_year = models.SmallIntegerField()
    reportid = models.IntegerField()
    version = models.SmallIntegerField()
    entity_type = models.ForeignKey(
        "DataDistroEntityTypes", models.DO_NOTHING, blank=True, null=True
    )
    fyenddate = models.DateField(blank=True, null=True)
    audittype = models.TextField()
    periodcovered = models.TextField(blank=True, null=True)
    numberofmonths = models.SmallIntegerField(blank=True, null=True)
    auditee_date_signed = models.DateField(blank=True, null=True)
    cpa_date_signed = models.DateField(blank=True, null=True)
    cog_agency = models.TextField(blank=True, null=True)
    oversight_agency = models.TextField(blank=True, null=True)
    completed_on = models.DateField(blank=True, null=True)
    previously_completed_on = models.DateField(blank=True, null=True)
    fac_accepted_date = models.DateField(blank=True, null=True)
    dollar_threshhold = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    total_federal_expenditure = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "data_distro_audits"


class DataDistroAwardFindings(models.Model):
    awardid = models.ForeignKey(
        "DataDistroAwards", models.DO_NOTHING, db_column="awardid"
    )
    fac_audit_id = models.BigIntegerField()
    findingrefnums = models.TextField(blank=True, null=True)
    type_requirement = models.TextField(blank=True, null=True)
    modified_opinion = models.TextField(blank=True, null=True)
    other_noncompliance = models.TextField(blank=True, null=True)
    material_weakness = models.TextField(blank=True, null=True)
    significant_deficiency = models.TextField(blank=True, null=True)
    other_findings = models.TextField(blank=True, null=True)
    qcosts = models.TextField(blank=True, null=True)
    repeat_finding = models.TextField(blank=True, null=True)
    priorfindingrefnums = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_award_findings"


class DataDistroAwardIndicators(models.Model):
    awardid = models.ForeignKey(
        "DataDistroAwards", models.DO_NOTHING, db_column="awardid"
    )
    rd = models.BooleanField(blank=True, null=True)
    loans = models.BooleanField(blank=True, null=True)
    direct = models.BooleanField(blank=True, null=True)
    arra = models.BooleanField(blank=True, null=True)
    major_program = models.BooleanField(blank=True, null=True)
    findings = models.TextField(blank=True, null=True)
    typereport_major_program = models.TextField(blank=True, null=True)
    type_requirement = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_award_indicators"


class DataDistroAwards(models.Model):
    auditid = models.ForeignKey(
        DataDistroAudits, models.DO_NOTHING, db_column="auditid"
    )
    cfda = models.TextField()
    award_identification = models.TextField(blank=True, null=True)
    loan_balance = models.TextField(blank=True, null=True)
    federal_program_name = models.TextField()
    amount = models.TextField()  # This field type is a guess.
    clustername = models.TextField(blank=True, null=True)
    stateclustername = models.TextField(blank=True, null=True)
    progam_total = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    cluster_total = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    passthrough_award = models.TextField(blank=True, null=True)
    passthrough_amount = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    findingrefnums = models.TextField(blank=True, null=True)
    findings_count = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_awards"


class DataDistroDuns(models.Model):
    dun = models.TextField()

    class Meta:
        managed = False
        db_table = "data_distro_duns"


class DataDistroEins(models.Model):
    ein = models.TextField()

    class Meta:
        managed = False
        db_table = "data_distro_eins"


class DataDistroEntityTypes(models.Model):
    identifier = models.SmallIntegerField()
    name = models.TextField()

    class Meta:
        managed = False
        db_table = "data_distro_entity_types"


class DataDistroFindingsText(models.Model):
    auditid = models.ForeignKey(
        DataDistroAudits, models.DO_NOTHING, db_column="auditid"
    )
    charts_tables = models.BooleanField(blank=True, null=True)
    text_value = models.TextField(blank=True, null=True)
    finding_ref_numbers = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_findings_text"


class DataDistroNotes(models.Model):
    typeid = models.ForeignKey(
        "DataDistroNotesType", models.DO_NOTHING, db_column="typeid"
    )
    auditid = models.ForeignKey(
        DataDistroAudits, models.DO_NOTHING, db_column="auditid"
    )
    content = models.TextField()
    note_index = models.SmallIntegerField()
    title = models.TextField()

    class Meta:
        managed = False
        db_table = "data_distro_notes"


class DataDistroNotesType(models.Model):
    name = models.TextField()

    class Meta:
        managed = False
        db_table = "data_distro_notes_type"


class DataDistroPassthroughs(models.Model):
    awardid = models.ForeignKey(
        DataDistroAwards, models.DO_NOTHING, db_column="awardid"
    )
    name = models.TextField(blank=True, null=True)
    passid = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_passthroughs"


class DataDistroPdfMetadata(models.Model):
    auditid = models.ForeignKey(
        DataDistroAudits, models.DO_NOTHING, db_column="auditid"
    )
    filename = models.TextField()
    searchable_threshold = models.SmallIntegerField(blank=True, null=True)
    searchable_type = models.TextField(blank=True, null=True)
    searchable_percentage = models.SmallIntegerField(blank=True, null=True)
    image_only_page_numbers = models.TextField(blank=True, null=True)
    processing_time_milliseconds = models.IntegerField(blank=True, null=True)
    upload_attempts = models.SmallIntegerField(blank=True, null=True)
    upload_status = models.TextField(blank=True, null=True)
    upload_date = models.DateTimeField()
    title = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    create_date = models.DateTimeField()
    modification_date = models.DateTimeField(blank=True, null=True)
    producer = models.TextField(blank=True, null=True)
    page_count = models.SmallIntegerField(blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)
    printable = models.BooleanField(blank=True, null=True)
    printable_high_quality = models.BooleanField(blank=True, null=True)
    modifiable = models.BooleanField(blank=True, null=True)
    err_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "data_distro_pdf_metadata"
