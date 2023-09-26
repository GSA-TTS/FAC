from peewee import *

database = SqliteDatabase('data/ay22/allfac22.sqlite3')

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Agency(BaseModel):
    agency = TextField(column_name='AGENCY', null=True)
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)

    class Meta:
        table_name = 'agency'
        primary_key = False

class Captext(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)

    class Meta:
        table_name = 'captext'
        primary_key = False

class CaptextFormatted(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)

    class Meta:
        table_name = 'captext_formatted'
        primary_key = False

class Cfda(BaseModel):
    amount = TextField(column_name='AMOUNT', null=True)
    arra = TextField(column_name='ARRA', null=True)
    audityear = TextField(column_name='AUDITYEAR', null=True)
    awardidentification = TextField(column_name='AWARDIDENTIFICATION', null=True)
    cfda = TextField(column_name='CFDA', null=True)
    cfdaprogramname = TextField(column_name='CFDAPROGRAMNAME', null=True)
    clustername = TextField(column_name='CLUSTERNAME', null=True)
    clustertotal = TextField(column_name='CLUSTERTOTAL', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    direct = TextField(column_name='DIRECT', null=True)
    ein = TextField(column_name='EIN', null=True)
    elecauditsid = TextField(column_name='ELECAUDITSID', null=True)
    federalprogramname = TextField(column_name='FEDERALPROGRAMNAME', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    findings = TextField(column_name='FINDINGS', null=True)
    findingscount = TextField(column_name='FINDINGSCOUNT', null=True)
    loanbalance = TextField(column_name='LOANBALANCE', null=True)
    loans = TextField(column_name='LOANS', null=True)
    majorprogram = TextField(column_name='MAJORPROGRAM', null=True)
    otherclustername = TextField(column_name='OTHERCLUSTERNAME', null=True)
    passthroughamount = TextField(column_name='PASSTHROUGHAMOUNT', null=True)
    passthroughaward = TextField(column_name='PASSTHROUGHAWARD', null=True)
    programtotal = TextField(column_name='PROGRAMTOTAL', null=True)
    qcosts2 = TextField(column_name='QCOSTS2', null=True)
    rd = TextField(column_name='RD', null=True)
    stateclustername = TextField(column_name='STATECLUSTERNAME', null=True)
    typereport_mp = TextField(column_name='TYPEREPORT_MP', null=True)
    typerequirement = TextField(column_name='TYPEREQUIREMENT', null=True)

    class Meta:
        table_name = 'cfda'
        primary_key = False

class Cpas(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    cpacity = TextField(column_name='CPACITY', null=True)
    cpacontact = TextField(column_name='CPACONTACT', null=True)
    cpaein = TextField(column_name='CPAEIN', null=True)
    cpaemail = TextField(column_name='CPAEMAIL', null=True)
    cpafax = TextField(column_name='CPAFAX', null=True)
    cpafirmname = TextField(column_name='CPAFIRMNAME', null=True)
    cpaphone = TextField(column_name='CPAPHONE', null=True)
    cpastate = TextField(column_name='CPASTATE', null=True)
    cpastreet1 = TextField(column_name='CPASTREET1', null=True)
    cpatitle = TextField(column_name='CPATITLE', null=True)
    cpazipcode = TextField(column_name='CPAZIPCODE', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)

    class Meta:
        table_name = 'cpas'
        primary_key = False

class Duns(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    duns = TextField(column_name='DUNS', null=True)
    dunseqnum = TextField(column_name='DUNSEQNUM', null=True)

    class Meta:
        table_name = 'duns'
        primary_key = False

class Eins(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    einseqnum = TextField(column_name='EINSEQNUM', null=True)

    class Meta:
        table_name = 'eins'
        primary_key = False

class Findings(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    elecauditfindingsid = TextField(column_name='ELECAUDITFINDINGSID', null=True)
    elecauditsid = TextField(column_name='ELECAUDITSID', null=True)
    findingsrefnums = TextField(column_name='FINDINGSREFNUMS', null=True)
    materialweakness = TextField(column_name='MATERIALWEAKNESS', null=True)
    modifiedopinion = TextField(column_name='MODIFIEDOPINION', null=True)
    otherfindings = TextField(column_name='OTHERFINDINGS', null=True)
    othernoncompliance = TextField(column_name='OTHERNONCOMPLIANCE', null=True)
    priorfindingrefnums = TextField(column_name='PRIORFINDINGREFNUMS', null=True)
    qcosts = TextField(column_name='QCOSTS', null=True)
    repeatfinding = TextField(column_name='REPEATFINDING', null=True)
    significantdeficiency = TextField(column_name='SIGNIFICANTDEFICIENCY', null=True)
    typerequirement = TextField(column_name='TYPEREQUIREMENT', null=True)

    class Meta:
        table_name = 'findings'
        primary_key = False

class Findingstext(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)

    class Meta:
        table_name = 'findingstext'
        primary_key = False

class FindingstextFormatted(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)

    class Meta:
        table_name = 'findingstext_formatted'
        primary_key = False

class Gen(BaseModel):
    auditeecontact = TextField(column_name='AUDITEECONTACT', null=True)
    auditeedatesigned = TextField(column_name='AUDITEEDATESIGNED', null=True)
    auditeeemail = TextField(column_name='AUDITEEEMAIL', null=True)
    auditeefax = TextField(column_name='AUDITEEFAX', null=True)
    auditeename = TextField(column_name='AUDITEENAME', null=True)
    auditeenametitle = TextField(column_name='AUDITEENAMETITLE', null=True)
    auditeephone = TextField(column_name='AUDITEEPHONE', null=True)
    auditeetitle = TextField(column_name='AUDITEETITLE', null=True)
    auditor_ein = TextField(column_name='AUDITOR_EIN', null=True)
    audittype = TextField(column_name='AUDITTYPE', null=True)
    audityear = TextField(column_name='AUDITYEAR', null=True)
    city = TextField(column_name='CITY', null=True)
    cogagency = TextField(column_name='COGAGENCY', null=True)
    cog_over = TextField(column_name='COG_OVER', null=True)
    cpacity = TextField(column_name='CPACITY', null=True)
    cpacontact = TextField(column_name='CPACONTACT', null=True)
    cpacountry = TextField(column_name='CPACOUNTRY', null=True)
    cpadatesigned = TextField(column_name='CPADATESIGNED', null=True)
    cpaemail = TextField(column_name='CPAEMAIL', null=True)
    cpafax = TextField(column_name='CPAFAX', null=True)
    cpafirmname = TextField(column_name='CPAFIRMNAME', null=True)
    cpaforeign = TextField(column_name='CPAFOREIGN', null=True)
    cpaphone = TextField(column_name='CPAPHONE', null=True)
    cpastate = TextField(column_name='CPASTATE', null=True)
    cpastreet1 = TextField(column_name='CPASTREET1', null=True)
    cpastreet2 = TextField(column_name='CPASTREET2', null=True)
    cpatitle = TextField(column_name='CPATITLE', null=True)
    cpazipcode = TextField(column_name='CPAZIPCODE', null=True)
    cyfindings = TextField(column_name='CYFINDINGS', null=True)
    datefirewall = TextField(column_name='DATEFIREWALL', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    dollarthreshold = TextField(column_name='DOLLARTHRESHOLD', null=True)
    duns = TextField(column_name='DUNS', null=True)
    dup_reports = TextField(column_name='DUP_REPORTS', null=True)
    ein = TextField(column_name='EIN', null=True)
    einsubcode = TextField(column_name='EINSUBCODE', null=True)
    entity_type = TextField(column_name='ENTITY_TYPE', null=True)
    facaccepteddate = TextField(column_name='FACACCEPTEDDATE', null=True)
    fyenddate = TextField(column_name='FYENDDATE', null=True)
    goingconcern = TextField(column_name='GOINGCONCERN', null=True)
    lowrisk = TextField(column_name='LOWRISK', null=True)
    materialnoncompliance = TextField(column_name='MATERIALNONCOMPLIANCE', null=True)
    materialweakness = TextField(column_name='MATERIALWEAKNESS', null=True)
    materialweakness_mp = TextField(column_name='MATERIALWEAKNESS_MP', null=True)
    multipleduns = TextField(column_name='MULTIPLEDUNS', null=True)
    multipleeins = TextField(column_name='MULTIPLEEINS', null=True)
    multipleueis = TextField(column_name='MULTIPLEUEIS', null=True)
    multiple_cpas = TextField(column_name='MULTIPLE_CPAS', null=True)
    numbermonths = TextField(column_name='NUMBERMONTHS', null=True)
    oversightagency = TextField(column_name='OVERSIGHTAGENCY', null=True)
    periodcovered = TextField(column_name='PERIODCOVERED', null=True)
    previousdatefirewall = TextField(column_name='PREVIOUSDATEFIREWALL', null=True)
    pyschedule = TextField(column_name='PYSCHEDULE', null=True)
    qcosts = TextField(column_name='QCOSTS', null=True)
    reportablecondition = TextField(column_name='REPORTABLECONDITION', null=True)
    reportablecondition_mp = TextField(column_name='REPORTABLECONDITION_MP', null=True)
    reportrequired = TextField(column_name='REPORTREQUIRED', null=True)
    sp_framework = TextField(column_name='SP_FRAMEWORK', null=True)
    sp_framework_required = TextField(column_name='SP_FRAMEWORK_REQUIRED', null=True)
    state = TextField(column_name='STATE', null=True)
    street1 = TextField(column_name='STREET1', null=True)
    street2 = TextField(column_name='STREET2', null=True)
    totfedexpend = TextField(column_name='TOTFEDEXPEND', null=True)
    typeofentity = TextField(column_name='TYPEOFENTITY', null=True)
    typereport_fs = TextField(column_name='TYPEREPORT_FS', null=True)
    typereport_mp = TextField(column_name='TYPEREPORT_MP', null=True)
    typereport_sp_framework = TextField(column_name='TYPEREPORT_SP_FRAMEWORK', null=True)
    uei = TextField(column_name='UEI', null=True)
    zipcode = TextField(column_name='ZIPCODE', null=True)

    class Meta:
        table_name = 'gen'
        primary_key = False

class Notes(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    content = TextField(column_name='CONTENT', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    id = TextField(column_name='ID', null=True)
    note_index = TextField(column_name='NOTE_INDEX', null=True)
    reportid = TextField(column_name='REPORTID', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    title = TextField(column_name='TITLE', null=True)
    type_id = TextField(column_name='TYPE_ID', null=True)
    version = TextField(column_name='VERSION', null=True)

    class Meta:
        table_name = 'notes'
        primary_key = False

class Passthrough(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    elecauditsid = TextField(column_name='ELECAUDITSID', null=True)
    passthroughid = TextField(column_name='PASSTHROUGHID', null=True)
    passthroughname = TextField(column_name='PASSTHROUGHNAME', null=True)

    class Meta:
        table_name = 'passthrough'
        primary_key = False

class Revisions(BaseModel):
    auditinfo = TextField(column_name='AUDITINFO', null=True)
    auditinfo_explain = TextField(column_name='AUDITINFO_EXPLAIN', null=True)
    audityear = TextField(column_name='AUDITYEAR', null=True)
    cap = TextField(column_name='CAP', null=True)
    cap_explain = TextField(column_name='CAP_EXPLAIN', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    elecrptrevisionid = TextField(column_name='ELECRPTREVISIONID', null=True)
    federalawards = TextField(column_name='FEDERALAWARDS', null=True)
    federalawards_explain = TextField(column_name='FEDERALAWARDS_EXPLAIN', null=True)
    findings = TextField(column_name='FINDINGS', null=True)
    findingstext = TextField(column_name='FINDINGSTEXT', null=True)
    findingstext_explain = TextField(column_name='FINDINGSTEXT_EXPLAIN', null=True)
    findings_explain = TextField(column_name='FINDINGS_EXPLAIN', null=True)
    geninfo = TextField(column_name='GENINFO', null=True)
    geninfo_explain = TextField(column_name='GENINFO_EXPLAIN', null=True)
    notestosefa = TextField(column_name='NOTESTOSEFA', null=True)
    notestosefa_explain = TextField(column_name='NOTESTOSEFA_EXPLAIN', null=True)
    other = TextField(column_name='OTHER', null=True)
    other_explain = TextField(column_name='OTHER_EXPLAIN', null=True)

    class Meta:
        table_name = 'revisions'
        primary_key = False

class Ueis(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    uei = TextField(column_name='UEI', null=True)
    ueiseqnum = TextField(column_name='UEISEQNUM', null=True)

    class Meta:
        table_name = 'ueis'
        primary_key = False

