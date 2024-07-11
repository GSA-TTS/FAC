from django.db import models
from django.utils import timezone


class ELECAUDITHEADER(models.Model):
    ELECAUDITHEADERID = models.TextField(blank=True, null=True)

    ID = models.TextField(blank=True, null=True)

    AUDITYEAR = models.TextField(blank=True, null=True)

    DBKEY = models.TextField(blank=True, null=True)

    FYENDDATE = models.TextField(blank=True, null=True)

    AUDITTYPE = models.TextField(blank=True, null=True)

    PERIODCOVERED = models.TextField(blank=True, null=True)

    NUMBERMONTHS = models.TextField(blank=True, null=True)

    MULTIPLEEINS = models.TextField(blank=True, null=True)

    EIN = models.TextField(blank=True, null=True)

    EINSUBCODE = models.TextField(blank=True, null=True)

    MULTIPLEDUNS = models.TextField(blank=True, null=True)

    DUNS = models.TextField(blank=True, null=True)

    AUDITEENAME = models.TextField(blank=True, null=True)

    STREET1 = models.TextField(blank=True, null=True)

    STREET2 = models.TextField(blank=True, null=True)

    CITY = models.TextField(blank=True, null=True)

    STATE = models.TextField(blank=True, null=True)

    ZIPCODE = models.TextField(blank=True, null=True)

    AUDITEECONTACT = models.TextField(blank=True, null=True)

    AUDITEETITLE = models.TextField(blank=True, null=True)

    AUDITEEPHONE = models.TextField(blank=True, null=True)

    AUDITEEFAX = models.TextField(blank=True, null=True)

    AUDITEEEMAIL = models.TextField(blank=True, null=True)

    AUDITEEDATESIGNED = models.TextField(blank=True, null=True)

    AUDITEENAMETITLE = models.TextField(blank=True, null=True)

    CPAFIRMNAME = models.TextField(blank=True, null=True)

    CPASTREET1 = models.TextField(blank=True, null=True)

    CPASTREET2 = models.TextField(blank=True, null=True)

    CPACITY = models.TextField(blank=True, null=True)

    CPASTATE = models.TextField(blank=True, null=True)

    CPAZIPCODE = models.TextField(blank=True, null=True)

    CPACONTACT = models.TextField(blank=True, null=True)

    CPATITLE = models.TextField(blank=True, null=True)

    CPAPHONE = models.TextField(blank=True, null=True)

    CPAFAX = models.TextField(blank=True, null=True)

    CPAEMAIL = models.TextField(blank=True, null=True)

    CPADATESIGNED = models.TextField(blank=True, null=True)

    CPANAMETITLE = models.TextField(blank=True, null=True)

    COG_OVER = models.TextField(blank=True, null=True)

    COGAGENCY = models.TextField(blank=True, null=True)

    TYPEREPORT_FS = models.TextField(blank=True, null=True)

    REPORTABLECONDITION = models.TextField(blank=True, null=True)

    MATERIALWEAKNESS = models.TextField(blank=True, null=True)

    MATERIALNONCOMPLIANCE = models.TextField(blank=True, null=True)

    GOINGCONCERN = models.TextField(blank=True, null=True)

    TYPEREPORT_MP = models.TextField(blank=True, null=True)

    DOLLARTHRESHOLD = models.TextField(blank=True, null=True)

    LOWRISK = models.TextField(blank=True, null=True)

    REPORTREQUIRED = models.TextField(blank=True, null=True)

    TOTFEDEXPEND = models.TextField(blank=True, null=True)

    COPIES = models.TextField(blank=True, null=True)

    REPORTABLECONDITION_MP = models.TextField(blank=True, null=True)

    MATERIALWEAKNESS_MP = models.TextField(blank=True, null=True)

    QCOSTS = models.TextField(blank=True, null=True)

    CYFINDINGS = models.TextField(blank=True, null=True)

    PYSCHEDULE = models.TextField(blank=True, null=True)

    DUP_REPORTS = models.TextField(blank=True, null=True)

    COG_AGENCY = models.TextField(blank=True, null=True)

    OVERSIGHTAGENCY = models.TextField(blank=True, null=True)

    DATERECEIVED = models.TextField(blank=True, null=True)

    DATEFIREWALL = models.TextField(blank=True, null=True)

    PREVIOUSDATEFIREWALL = models.TextField(blank=True, null=True)

    FINDINGREFNUM = models.TextField(blank=True, null=True)

    TYPEOFENTITY = models.TextField(blank=True, null=True)

    IMAGE = models.TextField(blank=True, null=True)

    AGENCYCFDA = models.TextField(blank=True, null=True)

    INITIALDATE = models.TextField(blank=True, null=True)

    DATERECEIVEDOTHER = models.TextField(blank=True, null=True)

    MULTIPLE_CPAS = models.TextField(blank=True, null=True)

    AUDITEECERTIFYNAME = models.TextField(blank=True, null=True)

    AUDITEECERTIFYTITLE = models.TextField(blank=True, null=True)

    FACACCEPTEDDATE = models.TextField(blank=True, null=True)

    AUDITOR_EIN = models.TextField(blank=True, null=True)

    SD_MATERIALWEAKNESS = models.TextField(blank=True, null=True)

    SD_MATERIALWEAKNESS_MP = models.TextField(blank=True, null=True)

    SIGNIFICANTDEFICIENCY = models.TextField(blank=True, null=True)

    SIGNIFICANTDEFICIENCY_MP = models.TextField(blank=True, null=True)

    SP_FRAMEWORK = models.TextField(blank=True, null=True)

    SP_FRAMEWORK_REQUIRED = models.TextField(blank=True, null=True)

    TYPEREPORT_SP_FRAMEWORK = models.TextField(blank=True, null=True)

    SUPPRESSION_CODE = models.TextField(blank=True, null=True)

    ENTITY_TYPE = models.TextField(blank=True, null=True)

    TYPEAUDIT_CODE = models.TextField(blank=True, null=True)

    OPEID = models.TextField(blank=True, null=True)

    DATETOED = models.TextField(blank=True, null=True)

    DATEFINISHED = models.TextField(blank=True, null=True)

    TYPEFINDING = models.TextField(blank=True, null=True)

    TYPEFUNDING = models.TextField(blank=True, null=True)

    FYSTARTDATE = models.TextField(blank=True, null=True)

    CPAFOREIGN = models.TextField(blank=True, null=True)

    UEI = models.TextField(blank=True, null=True)

    MULTIPLEUEIS = models.TextField(blank=True, null=True)

    CPACOUNTRY = models.TextField(blank=True, null=True)


class ELECEINS(models.Model):
    ID = models.TextField(blank=True, null=True)

    AUDITYEAR = models.TextField(blank=True, null=True)

    DBKEY = models.TextField(blank=True, null=True)

    EIN = models.TextField(blank=True, null=True)

    EINSEQNUM = models.TextField(blank=True, null=True)

    DUNS = models.TextField(blank=True, null=True)

    DUNSEQNUM = models.TextField(blank=True, null=True)


class ELECAUDITFINDINGS(models.Model):
    ELECAUDITFINDINGSID = models.TextField(blank=True, null=True)

    ELECAUDITSID = models.TextField(blank=True, null=True)

    AUDITYEAR = models.TextField(blank=True, null=True)

    DBKEY = models.TextField(blank=True, null=True)

    REPORTID = models.TextField(blank=True, null=True)

    VERSION = models.TextField(blank=True, null=True)

    QCOSTS = models.TextField(blank=True, null=True)

    OTHERFINDINGS = models.TextField(blank=True, null=True)

    SIGNIFICANTDEFICIENCY = models.TextField(blank=True, null=True)

    MATERIALWEAKNESS = models.TextField(blank=True, null=True)

    OTHERNONCOMPLIANCE = models.TextField(blank=True, null=True)

    TYPEREQUIREMENT = models.TextField(blank=True, null=True)

    FINDINGREFNUMS = models.TextField(blank=True, null=True)

    MODIFIEDOPINION = models.TextField(blank=True, null=True)

    REPEATFINDING = models.TextField(blank=True, null=True)

    PRIORFINDINGREFNUMS = models.TextField(blank=True, null=True)


class ELECNOTES(models.Model):
    ID = models.TextField(blank=True, null=True)

    REPORTID = models.TextField(blank=True, null=True)

    VERSION = models.TextField(blank=True, null=True)

    DBKEY = models.TextField(blank=True, null=True)

    AUDITYEAR = models.TextField(blank=True, null=True)

    SEQ_NUMBER = models.TextField(blank=True, null=True)

    TYPE_ID = models.TextField(blank=True, null=True)

    NOTE_INDEX = models.TextField(blank=True, null=True)

    TITLE = models.TextField(blank=True, null=True)

    CONTENT = models.TextField(blank=True, null=True)

    UEI = models.TextField(blank=True, null=True)

    MULTIPLEUEIS = models.TextField(blank=True, null=True)


class ELECFINDINGSTEXT(models.Model):
    SEQ_NUMBER = models.TextField(blank=True, null=True)

    DBKEY = models.TextField(blank=True, null=True)

    AUDITYEAR = models.TextField(blank=True, null=True)

    FINDINGREFNUMS = models.TextField(blank=True, null=True)

    TEXT = models.TextField(blank=True, null=True)

    CHARTSTABLES = models.TextField(blank=True, null=True)

    REPORTID = models.TextField(blank=True, null=True)

    VERSION = models.TextField(blank=True, null=True)

    UEI = models.TextField(blank=True, null=True)

    MULTIPLEUEIS = models.TextField(blank=True, null=True)


class ELECCPAS(models.Model):
    ID = models.TextField(blank=True, null=True)

    AUDITYEAR = models.TextField(blank=True, null=True)

    DBKEY = models.TextField(blank=True, null=True)

    SEQNUM = models.TextField(blank=True, null=True)

    VERSION = models.TextField(blank=True, null=True)

    CPAFIRMNAME = models.TextField(blank=True, null=True)

    CPASTREET1 = models.TextField(blank=True, null=True)

    CPACITY = models.TextField(blank=True, null=True)

    CPASTATE = models.TextField(blank=True, null=True)

    CPAZIPCODE = models.TextField(blank=True, null=True)

    CPACONTACT = models.TextField(blank=True, null=True)

    CPATITLE = models.TextField(blank=True, null=True)

    CPAPHONE = models.TextField(blank=True, null=True)

    CPAFAX = models.TextField(blank=True, null=True)

    CPAEMAIL = models.TextField(blank=True, null=True)

    CPAEIN = models.TextField(blank=True, null=True)


class ELECAUDITS(models.Model):
    ELECAUDITSID = models.TextField(blank=True, null=True)

    ID = models.TextField(blank=True, null=True)

    AUDITYEAR = models.TextField(blank=True, null=True)

    DBKEY = models.TextField(blank=True, null=True)

    CFDASEQNUM = models.TextField(blank=True, null=True)

    CFDA = models.TextField(blank=True, null=True)

    FEDERALPROGRAMNAME = models.TextField(blank=True, null=True)

    AMOUNT = models.TextField(blank=True, null=True)

    MAJORPROGRAM = models.TextField(blank=True, null=True)

    TYPEREQUIREMENT = models.TextField(blank=True, null=True)

    QCOSTS2 = models.TextField(blank=True, null=True)

    FINDINGS = models.TextField(blank=True, null=True)

    FINDINGREFNUMS = models.TextField(blank=True, null=True)

    RD = models.TextField(blank=True, null=True)

    DIRECT = models.TextField(blank=True, null=True)

    CFDA_PREFIX = models.TextField(blank=True, null=True)

    CFDA_EXT = models.TextField(blank=True, null=True)

    EIN = models.TextField(blank=True, null=True)

    CFDA2 = models.TextField(blank=True, null=True)

    TYPEREPORT_MP = models.TextField(blank=True, null=True)

    TYPEREPORT_MP_OVERRIDE = models.TextField(blank=True, null=True)

    ARRA = models.TextField(blank=True, null=True)

    LOANS = models.TextField(blank=True, null=True)

    FINDINGSCOUNT = models.TextField(blank=True, null=True)

    LOANBALANCE = models.TextField(blank=True, null=True)

    PASSTHROUGHAMOUNT = models.TextField(blank=True, null=True)

    AWARDIDENTIFICATION = models.TextField(blank=True, null=True)

    CLUSTERNAME = models.TextField(blank=True, null=True)

    PASSTHROUGHAWARD = models.TextField(blank=True, null=True)

    STATECLUSTERNAME = models.TextField(blank=True, null=True)

    PROGRAMTOTAL = models.TextField(blank=True, null=True)

    CLUSTERTOTAL = models.TextField(blank=True, null=True)

    OTHERCLUSTERNAME = models.TextField(blank=True, null=True)

    CFDAPROGRAMNAME = models.TextField(blank=True, null=True)

    UEI = models.TextField(blank=True, null=True)

    MULTIPLEUEIS = models.TextField(blank=True, null=True)


class ELECPASSTHROUGH(models.Model):
    ID = models.TextField(blank=True, null=True)

    AUDITYEAR = models.TextField(blank=True, null=True)

    DBKEY = models.TextField(blank=True, null=True)

    ELECAUDITSID = models.TextField(blank=True, null=True)

    PASSTHROUGHNAME = models.TextField(blank=True, null=True)

    PASSTHROUGHID = models.TextField(blank=True, null=True)


class ELECUEIS(models.Model):
    UEISID = models.TextField(blank=True, null=True)

    REPORTID = models.TextField(blank=True, null=True)

    VERSION = models.TextField(blank=True, null=True)

    DBKEY = models.TextField(blank=True, null=True)

    AUDITYEAR = models.TextField(blank=True, null=True)

    UEI = models.TextField(blank=True, null=True)

    SEQNUM = models.TextField(blank=True, null=True)


class ELECCAPTEXT(models.Model):
    SEQ_NUMBER = models.TextField(blank=True, null=True)

    DBKEY = models.TextField(blank=True, null=True)

    AUDITYEAR = models.TextField(blank=True, null=True)

    FINDINGREFNUMS = models.TextField(blank=True, null=True)

    TEXT = models.TextField(blank=True, null=True)

    CHARTSTABLES = models.TextField(blank=True, null=True)

    REPORTID = models.TextField(blank=True, null=True)

    VERSION = models.TextField(blank=True, null=True)

    UEI = models.TextField(blank=True, null=True)

    MULTIPLEUEIS = models.TextField(blank=True, null=True)


class ReportMigrationStatus(models.Model):
    audit_year = models.TextField(blank=True, null=True)
    dbkey = models.TextField(blank=True, null=True)
    run_datetime = models.DateTimeField(default=timezone.now)
    migration_status = models.TextField(blank=True, null=True)
    invalid_migration_tags = models.TextField(blank=True, null=True)
    skipped_validation_methods = models.TextField(blank=True, null=True)


class MigrationErrorDetail(models.Model):
    report_migration_status = models.ForeignKey(
        ReportMigrationStatus, on_delete=models.CASCADE
    )
    tag = models.TextField(blank=True, null=True)
    exception_class = models.TextField(blank=True, null=True)
    detail = models.TextField(blank=True, null=True)
