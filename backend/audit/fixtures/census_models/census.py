from peewee import (
    Model,
    TextField,
    BigIntegerField,
)
from playhouse.postgres_ext import PostgresqlDatabase

# FIXME: pull this from the config
database = PostgresqlDatabase("postgres", **{"host": "db", "user": "postgres"})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class CensusAgency16(BaseModel):
    agency = TextField(column_name='AGENCY', null=True)
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_agency16'
        schema = 'public'
        primary_key = False

class CensusAgency17(BaseModel):
    agency = TextField(column_name='AGENCY', null=True)
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_agency17'
        schema = 'public'
        primary_key = False

class CensusAgency18(BaseModel):
    agency = TextField(column_name='AGENCY', null=True)
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_agency18'
        schema = 'public'
        primary_key = False

class CensusAgency19(BaseModel):
    agency = TextField(column_name='AGENCY', null=True)
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_agency19'
        schema = 'public'
        primary_key = False

class CensusAgency20(BaseModel):
    agency = TextField(column_name='AGENCY', null=True)
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_agency20'
        schema = 'public'
        primary_key = False

class CensusAgency21(BaseModel):
    agency = TextField(column_name='AGENCY', null=True)
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_agency21'
        schema = 'public'
        primary_key = False

class CensusAgency22(BaseModel):
    agency = TextField(column_name='AGENCY', null=True)
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_agency22'
        schema = 'public'
        primary_key = False

class CensusCaptext19(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_captext19'
        schema = 'public'
        primary_key = False

class CensusCaptext20(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_captext20'
        schema = 'public'
        primary_key = False

class CensusCaptext21(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_captext21'
        schema = 'public'
        primary_key = False

class CensusCaptext22(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_captext22'
        schema = 'public'
        primary_key = False

class CensusCaptextFormatted19(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_captext_formatted19'
        schema = 'public'
        primary_key = False

class CensusCaptextFormatted20(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_captext_formatted20'
        schema = 'public'
        primary_key = False

class CensusCaptextFormatted21(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_captext_formatted21'
        schema = 'public'
        primary_key = False

class CensusCaptextFormatted22(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_captext_formatted22'
        schema = 'public'
        primary_key = False

class CensusCfda16(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cfda16'
        schema = 'public'
        primary_key = False

class CensusCfda17(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cfda17'
        schema = 'public'
        primary_key = False

class CensusCfda18(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cfda18'
        schema = 'public'
        primary_key = False

class CensusCfda19(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cfda19'
        schema = 'public'
        primary_key = False

class CensusCfda20(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cfda20'
        schema = 'public'
        primary_key = False

class CensusCfda21(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cfda21'
        schema = 'public'
        primary_key = False

class CensusCfda22(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cfda22'
        schema = 'public'
        primary_key = False

class CensusCpas16(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cpas16'
        schema = 'public'
        primary_key = False

class CensusCpas17(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cpas17'
        schema = 'public'
        primary_key = False

class CensusCpas18(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cpas18'
        schema = 'public'
        primary_key = False

class CensusCpas19(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cpas19'
        schema = 'public'
        primary_key = False

class CensusCpas20(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cpas20'
        schema = 'public'
        primary_key = False

class CensusCpas21(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cpas21'
        schema = 'public'
        primary_key = False

class CensusCpas22(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_cpas22'
        schema = 'public'
        primary_key = False

class CensusDuns16(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    duns = TextField(column_name='DUNS', null=True)
    dunseqnum = TextField(column_name='DUNSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_duns16'
        schema = 'public'
        primary_key = False

class CensusDuns17(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    duns = TextField(column_name='DUNS', null=True)
    dunseqnum = TextField(column_name='DUNSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_duns17'
        schema = 'public'
        primary_key = False

class CensusDuns18(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    duns = TextField(column_name='DUNS', null=True)
    dunseqnum = TextField(column_name='DUNSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_duns18'
        schema = 'public'
        primary_key = False

class CensusDuns19(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    duns = TextField(column_name='DUNS', null=True)
    dunseqnum = TextField(column_name='DUNSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_duns19'
        schema = 'public'
        primary_key = False

class CensusDuns20(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    duns = TextField(column_name='DUNS', null=True)
    dunseqnum = TextField(column_name='DUNSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_duns20'
        schema = 'public'
        primary_key = False

class CensusDuns21(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    duns = TextField(column_name='DUNS', null=True)
    dunseqnum = TextField(column_name='DUNSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_duns21'
        schema = 'public'
        primary_key = False

class CensusDuns22(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    duns = TextField(column_name='DUNS', null=True)
    dunseqnum = TextField(column_name='DUNSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_duns22'
        schema = 'public'
        primary_key = False

class CensusEins16(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    einseqnum = TextField(column_name='EINSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_eins16'
        schema = 'public'
        primary_key = False

class CensusEins17(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    einseqnum = TextField(column_name='EINSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_eins17'
        schema = 'public'
        primary_key = False

class CensusEins18(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    einseqnum = TextField(column_name='EINSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_eins18'
        schema = 'public'
        primary_key = False

class CensusEins19(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    einseqnum = TextField(column_name='EINSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_eins19'
        schema = 'public'
        primary_key = False

class CensusEins20(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    einseqnum = TextField(column_name='EINSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_eins20'
        schema = 'public'
        primary_key = False

class CensusEins21(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    einseqnum = TextField(column_name='EINSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_eins21'
        schema = 'public'
        primary_key = False

class CensusEins22(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    ein = TextField(column_name='EIN', null=True)
    einseqnum = TextField(column_name='EINSEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_eins22'
        schema = 'public'
        primary_key = False

class CensusFindings16(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findings16'
        schema = 'public'
        primary_key = False

class CensusFindings17(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findings17'
        schema = 'public'
        primary_key = False

class CensusFindings18(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findings18'
        schema = 'public'
        primary_key = False

class CensusFindings19(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findings19'
        schema = 'public'
        primary_key = False

class CensusFindings20(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findings20'
        schema = 'public'
        primary_key = False

class CensusFindings21(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findings21'
        schema = 'public'
        primary_key = False

class CensusFindings22(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findings22'
        schema = 'public'
        primary_key = False

class CensusFindingstext19(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findingstext19'
        schema = 'public'
        primary_key = False

class CensusFindingstext20(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findingstext20'
        schema = 'public'
        primary_key = False

class CensusFindingstext21(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findingstext21'
        schema = 'public'
        primary_key = False

class CensusFindingstext22(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findingstext22'
        schema = 'public'
        primary_key = False

class CensusFindingstextFormatted19(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findingstext_formatted19'
        schema = 'public'
        primary_key = False

class CensusFindingstextFormatted20(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findingstext_formatted20'
        schema = 'public'
        primary_key = False

class CensusFindingstextFormatted21(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findingstext_formatted21'
        schema = 'public'
        primary_key = False

class CensusFindingstextFormatted22(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    chartstables = TextField(column_name='CHARTSTABLES', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    findingrefnums = TextField(column_name='FINDINGREFNUMS', null=True)
    seq_number = TextField(column_name='SEQ_NUMBER', null=True)
    text = TextField(column_name='TEXT', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_findingstext_formatted22'
        schema = 'public'
        primary_key = False

class CensusGen16(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_gen16'
        schema = 'public'
        primary_key = False

class CensusGen17(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_gen17'
        schema = 'public'
        primary_key = False

class CensusGen18(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_gen18'
        schema = 'public'
        primary_key = False

class CensusGen19(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_gen19'
        schema = 'public'
        primary_key = False

class CensusGen20(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_gen20'
        schema = 'public'
        primary_key = False

class CensusGen21(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_gen21'
        schema = 'public'
        primary_key = False

class CensusGen22(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_gen22'
        schema = 'public'
        primary_key = False

class CensusNotes19(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_notes19'
        schema = 'public'
        primary_key = False

class CensusNotes20(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_notes20'
        schema = 'public'
        primary_key = False

class CensusNotes21(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_notes21'
        schema = 'public'
        primary_key = False

class CensusNotes22(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_notes22'
        schema = 'public'
        primary_key = False

class CensusPassthrough16(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    elecauditsid = TextField(column_name='ELECAUDITSID', null=True)
    passthroughid = TextField(column_name='PASSTHROUGHID', null=True)
    passthroughname = TextField(column_name='PASSTHROUGHNAME', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_passthrough16'
        schema = 'public'
        primary_key = False

class CensusPassthrough17(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    elecauditsid = TextField(column_name='ELECAUDITSID', null=True)
    passthroughid = TextField(column_name='PASSTHROUGHID', null=True)
    passthroughname = TextField(column_name='PASSTHROUGHNAME', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_passthrough17'
        schema = 'public'
        primary_key = False

class CensusPassthrough18(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    elecauditsid = TextField(column_name='ELECAUDITSID', null=True)
    passthroughid = TextField(column_name='PASSTHROUGHID', null=True)
    passthroughname = TextField(column_name='PASSTHROUGHNAME', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_passthrough18'
        schema = 'public'
        primary_key = False

class CensusPassthrough19(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    elecauditsid = TextField(column_name='ELECAUDITSID', null=True)
    passthroughid = TextField(column_name='PASSTHROUGHID', null=True)
    passthroughname = TextField(column_name='PASSTHROUGHNAME', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_passthrough19'
        schema = 'public'
        primary_key = False

class CensusPassthrough20(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    elecauditsid = TextField(column_name='ELECAUDITSID', null=True)
    passthroughid = TextField(column_name='PASSTHROUGHID', null=True)
    passthroughname = TextField(column_name='PASSTHROUGHNAME', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_passthrough20'
        schema = 'public'
        primary_key = False

class CensusPassthrough21(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    elecauditsid = TextField(column_name='ELECAUDITSID', null=True)
    passthroughid = TextField(column_name='PASSTHROUGHID', null=True)
    passthroughname = TextField(column_name='PASSTHROUGHNAME', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_passthrough21'
        schema = 'public'
        primary_key = False

class CensusPassthrough22(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    elecauditsid = TextField(column_name='ELECAUDITSID', null=True)
    passthroughid = TextField(column_name='PASSTHROUGHID', null=True)
    passthroughname = TextField(column_name='PASSTHROUGHNAME', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_passthrough22'
        schema = 'public'
        primary_key = False

class CensusRevisions19(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_revisions19'
        schema = 'public'
        primary_key = False

class CensusRevisions20(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_revisions20'
        schema = 'public'
        primary_key = False

class CensusRevisions21(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_revisions21'
        schema = 'public'
        primary_key = False

class CensusRevisions22(BaseModel):
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
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_revisions22'
        schema = 'public'
        primary_key = False

class CensusUeis22(BaseModel):
    audityear = TextField(column_name='AUDITYEAR', null=True)
    dbkey = TextField(column_name='DBKEY', null=True)
    uei = TextField(column_name='UEI', null=True)
    ueiseqnum = TextField(column_name='UEISEQNUM', null=True)
    index = BigIntegerField(index=True, null=True)

    class Meta:
        table_name = 'census_ueis22'
        schema = 'public'
        primary_key = False
