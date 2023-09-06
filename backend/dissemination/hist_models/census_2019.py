from django.db import models


class CensusCfda19(models.Model):
    index = models.BigIntegerField(blank=True, primary_key=True)
    audityear = models.TextField(
        db_column="AUDITYEAR", blank=True, null=True
    )  # Field name made lowercase.
    dbkey = models.TextField(
        db_column="DBKEY", blank=True, null=True
    )  # Field name made lowercase.
    ein = models.TextField(
        db_column="EIN", blank=True, null=True
    )  # Field name made lowercase.
    cfda = models.TextField(
        db_column="CFDA", blank=True, null=True
    )  # Field name made lowercase.
    awardidentification = models.TextField(
        db_column="AWARDIDENTIFICATION", blank=True, null=True
    )  # Field name made lowercase.
    rd = models.TextField(
        db_column="RD", blank=True, null=True
    )  # Field name made lowercase.
    federalprogramname = models.TextField(
        db_column="FEDERALPROGRAMNAME", blank=True, null=True
    )  # Field name made lowercase.
    amount = models.TextField(
        db_column="AMOUNT", blank=True, null=True
    )  # Field name made lowercase.
    clustername = models.TextField(
        db_column="CLUSTERNAME", blank=True, null=True
    )  # Field name made lowercase.
    stateclustername = models.TextField(
        db_column="STATECLUSTERNAME", blank=True, null=True
    )  # Field name made lowercase.
    programtotal = models.TextField(
        db_column="PROGRAMTOTAL", blank=True, null=True
    )  # Field name made lowercase.
    clustertotal = models.TextField(
        db_column="CLUSTERTOTAL", blank=True, null=True
    )  # Field name made lowercase.
    direct = models.TextField(
        db_column="DIRECT", blank=True, null=True
    )  # Field name made lowercase.
    passthroughaward = models.TextField(
        db_column="PASSTHROUGHAWARD", blank=True, null=True
    )  # Field name made lowercase.
    passthroughamount = models.TextField(
        db_column="PASSTHROUGHAMOUNT", blank=True, null=True
    )  # Field name made lowercase.
    majorprogram = models.TextField(
        db_column="MAJORPROGRAM", blank=True, null=True
    )  # Field name made lowercase.
    typereport_mp = models.TextField(
        db_column="TYPEREPORT_MP", blank=True, null=True
    )  # Field name made lowercase.
    typerequirement = models.TextField(
        db_column="TYPEREQUIREMENT", blank=True, null=True
    )  # Field name made lowercase.
    qcosts2 = models.TextField(
        db_column="QCOSTS2", blank=True, null=True
    )  # Field name made lowercase.
    findings = models.TextField(
        db_column="FINDINGS", blank=True, null=True
    )  # Field name made lowercase.
    findingrefnums = models.TextField(
        db_column="FINDINGREFNUMS", blank=True, null=True
    )  # Field name made lowercase.
    arra = models.TextField(
        db_column="ARRA", blank=True, null=True
    )  # Field name made lowercase.
    loans = models.TextField(
        db_column="LOANS", blank=True, null=True
    )  # Field name made lowercase.
    loanbalance = models.TextField(
        db_column="LOANBALANCE", blank=True, null=True
    )  # Field name made lowercase.
    findingscount = models.TextField(
        db_column="FINDINGSCOUNT", blank=True, null=True
    )  # Field name made lowercase.
    elecauditsid = models.TextField(
        db_column="ELECAUDITSID", blank=True, null=True
    )  # Field name made lowercase.
    otherclustername = models.TextField(
        db_column="OTHERCLUSTERNAME", blank=True, null=True
    )  # Field name made lowercase.
    cfdaprogramname = models.TextField(
        db_column="CFDAPROGRAMNAME", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "census_cfda19"


class CensusGen19(models.Model):
    index = models.BigIntegerField(blank=True, primary_key=True)
    audityear = models.TextField(
        db_column="AUDITYEAR", blank=True, null=True
    )  # Field name made lowercase.
    dbkey = models.TextField(
        db_column="DBKEY", blank=True, null=True
    )  # Field name made lowercase.
    typeofentity = models.TextField(
        db_column="TYPEOFENTITY", blank=True, null=True
    )  # Field name made lowercase.
    fyenddate = models.TextField(
        db_column="FYENDDATE", blank=True, null=True
    )  # Field name made lowercase.
    audittype = models.TextField(
        db_column="AUDITTYPE", blank=True, null=True
    )  # Field name made lowercase.
    periodcovered = models.TextField(
        db_column="PERIODCOVERED", blank=True, null=True
    )  # Field name made lowercase.
    numbermonths = models.TextField(
        db_column="NUMBERMONTHS", blank=True, null=True
    )  # Field name made lowercase.
    ein = models.TextField(
        db_column="EIN", blank=True, null=True
    )  # Field name made lowercase.
    multipleeins = models.TextField(
        db_column="MULTIPLEEINS", blank=True, null=True
    )  # Field name made lowercase.
    einsubcode = models.TextField(
        db_column="EINSUBCODE", blank=True, null=True
    )  # Field name made lowercase.
    duns = models.TextField(
        db_column="DUNS", blank=True, null=True
    )  # Field name made lowercase.
    multipleduns = models.TextField(
        db_column="MULTIPLEDUNS", blank=True, null=True
    )  # Field name made lowercase.
    auditeename = models.TextField(
        db_column="AUDITEENAME", blank=True, null=True
    )  # Field name made lowercase.
    street1 = models.TextField(
        db_column="STREET1", blank=True, null=True
    )  # Field name made lowercase.
    street2 = models.TextField(
        db_column="STREET2", blank=True, null=True
    )  # Field name made lowercase.
    city = models.TextField(
        db_column="CITY", blank=True, null=True
    )  # Field name made lowercase.
    state = models.TextField(
        db_column="STATE", blank=True, null=True
    )  # Field name made lowercase.
    zipcode = models.TextField(
        db_column="ZIPCODE", blank=True, null=True
    )  # Field name made lowercase.
    auditeecontact = models.TextField(
        db_column="AUDITEECONTACT", blank=True, null=True
    )  # Field name made lowercase.
    auditeetitle = models.TextField(
        db_column="AUDITEETITLE", blank=True, null=True
    )  # Field name made lowercase.
    auditeephone = models.TextField(
        db_column="AUDITEEPHONE", blank=True, null=True
    )  # Field name made lowercase.
    auditeefax = models.TextField(
        db_column="AUDITEEFAX", blank=True, null=True
    )  # Field name made lowercase.
    auditeeemail = models.TextField(
        db_column="AUDITEEEMAIL", blank=True, null=True
    )  # Field name made lowercase.
    auditeedatesigned = models.TextField(
        db_column="AUDITEEDATESIGNED", blank=True, null=True
    )  # Field name made lowercase.
    auditeenametitle = models.TextField(
        db_column="AUDITEENAMETITLE", blank=True, null=True
    )  # Field name made lowercase.
    cpafirmname = models.TextField(
        db_column="CPAFIRMNAME", blank=True, null=True
    )  # Field name made lowercase.
    cpastreet1 = models.TextField(
        db_column="CPASTREET1", blank=True, null=True
    )  # Field name made lowercase.
    cpastreet2 = models.TextField(
        db_column="CPASTREET2", blank=True, null=True
    )  # Field name made lowercase.
    cpacity = models.TextField(
        db_column="CPACITY", blank=True, null=True
    )  # Field name made lowercase.
    cpastate = models.TextField(
        db_column="CPASTATE", blank=True, null=True
    )  # Field name made lowercase.
    cpazipcode = models.TextField(
        db_column="CPAZIPCODE", blank=True, null=True
    )  # Field name made lowercase.
    cpacontact = models.TextField(
        db_column="CPACONTACT", blank=True, null=True
    )  # Field name made lowercase.
    cpatitle = models.TextField(
        db_column="CPATITLE", blank=True, null=True
    )  # Field name made lowercase.
    cpaphone = models.TextField(
        db_column="CPAPHONE", blank=True, null=True
    )  # Field name made lowercase.
    cpafax = models.TextField(
        db_column="CPAFAX", blank=True, null=True
    )  # Field name made lowercase.
    cpaemail = models.TextField(
        db_column="CPAEMAIL", blank=True, null=True
    )  # Field name made lowercase.
    cpadatesigned = models.TextField(
        db_column="CPADATESIGNED", blank=True, null=True
    )  # Field name made lowercase.
    cog_over = models.TextField(
        db_column="COG_OVER", blank=True, null=True
    )  # Field name made lowercase.
    cogagency = models.TextField(
        db_column="COGAGENCY", blank=True, null=True
    )  # Field name made lowercase.
    oversightagency = models.TextField(
        db_column="OVERSIGHTAGENCY", blank=True, null=True
    )  # Field name made lowercase.
    typereport_fs = models.TextField(
        db_column="TYPEREPORT_FS", blank=True, null=True
    )  # Field name made lowercase.
    sp_framework = models.TextField(
        db_column="SP_FRAMEWORK", blank=True, null=True
    )  # Field name made lowercase.
    sp_framework_required = models.TextField(
        db_column="SP_FRAMEWORK_REQUIRED", blank=True, null=True
    )  # Field name made lowercase.
    typereport_sp_framework = models.TextField(
        db_column="TYPEREPORT_SP_FRAMEWORK", blank=True, null=True
    )  # Field name made lowercase.
    goingconcern = models.TextField(
        db_column="GOINGCONCERN", blank=True, null=True
    )  # Field name made lowercase.
    reportablecondition = models.TextField(
        db_column="REPORTABLECONDITION", blank=True, null=True
    )  # Field name made lowercase.
    materialweakness = models.TextField(
        db_column="MATERIALWEAKNESS", blank=True, null=True
    )  # Field name made lowercase.
    materialnoncompliance = models.TextField(
        db_column="MATERIALNONCOMPLIANCE", blank=True, null=True
    )  # Field name made lowercase.
    typereport_mp = models.TextField(
        db_column="TYPEREPORT_MP", blank=True, null=True
    )  # Field name made lowercase.
    dup_reports = models.TextField(
        db_column="DUP_REPORTS", blank=True, null=True
    )  # Field name made lowercase.
    dollarthreshold = models.TextField(
        db_column="DOLLARTHRESHOLD", blank=True, null=True
    )  # Field name made lowercase.
    lowrisk = models.TextField(
        db_column="LOWRISK", blank=True, null=True
    )  # Field name made lowercase.
    reportablecondition_mp = models.TextField(
        db_column="REPORTABLECONDITION_MP", blank=True, null=True
    )  # Field name made lowercase.
    materialweakness_mp = models.TextField(
        db_column="MATERIALWEAKNESS_MP", blank=True, null=True
    )  # Field name made lowercase.
    qcosts = models.TextField(
        db_column="QCOSTS", blank=True, null=True
    )  # Field name made lowercase.
    cyfindings = models.TextField(
        db_column="CYFINDINGS", blank=True, null=True
    )  # Field name made lowercase.
    pyschedule = models.TextField(
        db_column="PYSCHEDULE", blank=True, null=True
    )  # Field name made lowercase.
    totfedexpend = models.TextField(
        db_column="TOTFEDEXPEND", blank=True, null=True
    )  # Field name made lowercase.
    datefirewall = models.TextField(
        db_column="DATEFIREWALL", blank=True, null=True
    )  # Field name made lowercase.
    previousdatefirewall = models.TextField(
        db_column="PREVIOUSDATEFIREWALL", blank=True, null=True
    )  # Field name made lowercase.
    reportrequired = models.TextField(
        db_column="REPORTREQUIRED", blank=True, null=True
    )  # Field name made lowercase.
    multiple_cpas = models.TextField(
        db_column="MULTIPLE_CPAS", blank=True, null=True
    )  # Field name made lowercase.
    auditor_ein = models.TextField(
        db_column="AUDITOR_EIN", blank=True, null=True
    )  # Field name made lowercase.
    facaccepteddate = models.TextField(
        db_column="FACACCEPTEDDATE", blank=True, null=True
    )  # Field name made lowercase.
    cpaforeign = models.TextField(
        db_column="CPAFOREIGN", blank=True, null=True
    )  # Field name made lowercase.
    cpacountry = models.TextField(
        db_column="CPACOUNTRY", blank=True, null=True
    )  # Field name made lowercase.
    entity_type = models.TextField(
        db_column="ENTITY_TYPE", blank=True, null=True
    )  # Field name made lowercase.
    uei = models.TextField(
        db_column="UEI", blank=True, null=True
    )  # Field name made lowercase.
    multipleueis = models.TextField(
        db_column="MULTIPLEUEIS", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "census_gen19"
