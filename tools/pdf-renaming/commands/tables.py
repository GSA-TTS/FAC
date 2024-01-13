import sqlite3
import argparse
import re
import logging
from peewee import *
from playhouse.sqliteq import SqliteQueueDatabase
import atexit

logger = logging.getLogger(__name__)

null = None
audit_table_template = {
		"ELECAUDITHEADERID" : 1476149,
		"ID" : "3132022",
		"AUDITYEAR" : "2022",
		"DBKEY" : 313,
		"FYENDDATE" : "2022-09-30",
		"AUDITTYPE" : "S",
		"PERIODCOVERED" : "A",
		"NUMERICMONTHS" : null,
		"MULTIPLEEINS" : "N",
		"EIN" : "010318051",
		"EINSUBCODE" : null,
		"MULTIPLEDUNS" : "N",
		"DUNS" : "196450548",
		"AUDITEENAME" : "CENTRAL MAINE AREA AGENCY ON AGING D\/B\/A SPECTRUM GENERATIONS",
		"STREET1" : "1 WESTON COURT",
		"STREET2" : null,
		"CITY" : "AUGUSTA",
		"STATE" : "ME",
		"ZIPCODE" : "04330",
		"AUDITEECONTACT" : "SHARON CLEVELAND",
		"AUDITEETITLE" : "CHIEF FINANCIAL OFFICER",
		"AUDITEEPHONE" : "2076201664",
		"AUDITEEFAX" : null,
		"AUDITEEEMAIL" : "SCLEVELAND@SPECTRUMGENERATIONS.ORG",
		"AUDITEEDATESIGNED" : "2023-04-03",
		"AUDITEENAMETITLE" : "SHARON CLEVELAND-CFO",
		"CPAFIRMNAME" : "WIPFLI LLP",
		"CPASTREET1" : "30 LONG CREEK DRIVE",
		"CPASTREET2" : null,
		"CPACITY" : "SOUTH PORTLAND",
		"CPASTATE" : "ME",
		"CPAZIPCODE" : "04106",
		"CPACONTACT" : "DANIELLE MARTIN",
		"CPATITLE" : "SENIOR MANAGER",
		"CPAPHONE" : "2075123427",
		"CPAFAX" : null,
		"CPAEMAIL" : "DANIELLE.MARTIN@WIPFLI.COM",
		"CPADATESIGNED" : "2023-03-03",
		"CPANAMETITLE" : null,
		"COG_OVER" : "O",
		"COGAGENCY" : null,
		"TYPEREPORT_FS" : "U",
		"REPORTABLECONDITION" : "N",
		"MATERIALWEAKNESS" : "N",
		"MATERIALNONCOMPLIANCE" : "N",
		"GOINGCONCERN" : "N",
		"TYPEREPORT_MP" : "U",
		"DOLLARTHRESHOLD" : 750000,
		"LOWRISK" : "Y",
		"REPORTREQUIRED" : null,
		"TOTFEDEXPEND" : 4161167,
		"COPIES" : null,
		"REPORTABLECONDITION_MP" : "N",
		"MATERIALWEAKNESS_MP" : "N",
		"QCOSTS" : "N",
		"CYFINDINGS" : "N",
		"PYSCHEDULE" : "N",
		"DUP_REPORTS" : "N",
		"COG_AGENCY" : null,
		"OVERSIGHTAGENCY" : "93",
		"DATERECEIVED" : "2023-04-03",
		"DATEFIREWALL" : "2023-04-07",
		"PREVIOUSDATEFIREWALL" : null,
		"FINDINGREFNUM" : "N",
		"TYPEOFENTITY" : "908",
		"IMAGE" : 1,
		"AGENCYCFDA" : "x00",
		"INITIALDATE" : "2023-04-03",
		"DATERECEIVEDOTHER" : null,
		"MULTIPLE_CPAS" : "N",
		"AUDITEECERTIFYNAME" : "SHARON CLEVELAND",
		"AUDITEECERTIFYTITLE" : "CFO",
		"FACACCEPTEDDATE" : "2023-04-03",
		"AUDITOR_EIN" : "390758449",
		"SD_MATERIALWEAKNESS" : "N",
		"SD_MATERIALWEAKNESS_MP" : null,
		"SIGNIFICANTDEFICIENCY" : "N",
		"SIGNIFICANTDEFICIENCY_MP" : "N",
		"SP_FRAMEWORK" : null,
		"SP_FRAMEWORK_REQUIRED" : null,
		"TYPEREPORT_SP_FRAMEWORK" : null,
		"SUPPRESSION_CODE" : null,
		"ENTITY_TYPE" : "Non-profit",
		"TYPEAUDIT_CODE" : "UG",
		"OPEID" : null,
		"DATETOED" : null,
		"DATEFINISHED" : null,
		"TYPEFINDING" : null,
		"TYPEFUNDING" : null,
		"FYSTARTDATE" : "2021-10-01",
		"CPAFOREIGN" : null,
		"UEI" : "GTTUP55GN2U3",
		"MULTIPLEUEIS" : "N",
		"CPACOUNTRY" : "US"
	}

ims_table_template = {
		"ID" : "223652022",
		"ID2" : "01949635",
		"DBKEY" : 22365,
		"AUDITYEAR" : "2022",
		"REPORTID" : 949635,
		"VERSION" : 1,
		"TYPEAUDIT_CODE" : "UG",
		"SUPPRESSION_CODE" : null,
		"IMAGE_EXISTS" : "1"
	}


database_proxy = DatabaseProxy()  # Create a proxy for our db.

def setup_database(db_filename):
    database = SqliteQueueDatabase(db_filename)
    database_proxy.initialize(database)
    Renaming().create_table()

def setup_postgres_database():
    database = PostgresqlDatabase('postgres', host='localhost', user='postgres')
    database_proxy.initialize(database)
    Renaming().create_table()


class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database_proxy

class Audit(BaseModel):

    agencycfda = BareField(column_name='AGENCYCFDA', null=True)
    auditeecertifyname = BareField(column_name='AUDITEECERTIFYNAME', null=True)
    auditeecertifytitle = BareField(column_name='AUDITEECERTIFYTITLE', null=True)
    auditeecontact = BareField(column_name='AUDITEECONTACT', null=True)
    auditeedatesigned = BareField(column_name='AUDITEEDATESIGNED', null=True)
    auditeeemail = BareField(column_name='AUDITEEEMAIL', null=True)
    auditeefax = BareField(column_name='AUDITEEFAX', null=True)
    auditeename = BareField(column_name='AUDITEENAME', null=True)
    auditeenametitle = BareField(column_name='AUDITEENAMETITLE', null=True)
    auditeephone = BareField(column_name='AUDITEEPHONE', null=True)
    auditeetitle = BareField(column_name='AUDITEETITLE', null=True)
    auditor_ein = BareField(column_name='AUDITOR_EIN', null=True)
    audittype = BareField(column_name='AUDITTYPE', null=True)
    audityear = BareField(column_name='AUDITYEAR', null=True, index=True)
    city = BareField(column_name='CITY', null=True)
    cogagency = BareField(column_name='COGAGENCY', null=True)
    cog_agency = BareField(column_name='COG_AGENCY', null=True)
    cog_over = BareField(column_name='COG_OVER', null=True)
    copies = BareField(column_name='COPIES', null=True)
    cpacity = BareField(column_name='CPACITY', null=True)
    cpacontact = BareField(column_name='CPACONTACT', null=True)
    cpacountry = BareField(column_name='CPACOUNTRY', null=True)
    cpadatesigned = BareField(column_name='CPADATESIGNED', null=True)
    cpaemail = BareField(column_name='CPAEMAIL', null=True)
    cpafax = BareField(column_name='CPAFAX', null=True)
    cpafirmname = BareField(column_name='CPAFIRMNAME', null=True)
    cpaforeign = BareField(column_name='CPAFOREIGN', null=True)
    cpanametitle = BareField(column_name='CPANAMETITLE', null=True)
    cpaphone = BareField(column_name='CPAPHONE', null=True)
    cpastate = BareField(column_name='CPASTATE', null=True)
    cpastreet1 = BareField(column_name='CPASTREET1', null=True)
    cpastreet2 = BareField(column_name='CPASTREET2', null=True)
    cpatitle = BareField(column_name='CPATITLE', null=True)
    cpazipcode = BareField(column_name='CPAZIPCODE', null=True)
    cyfindings = BareField(column_name='CYFINDINGS', null=True)
    datefinished = BareField(column_name='DATEFINISHED', null=True)
    datefirewall = BareField(column_name='DATEFIREWALL', null=True)
    datereceived = BareField(column_name='DATERECEIVED', null=True)
    datereceivedother = BareField(column_name='DATERECEIVEDOTHER', null=True)
    datetoed = BareField(column_name='DATETOED', null=True)
    dbkey = BareField(column_name='DBKEY', null=True, index=True)
    dollarthreshold = BareField(column_name='DOLLARTHRESHOLD', null=True)
    duns = BareField(column_name='DUNS', null=True)
    dup_reports = BareField(column_name='DUP_REPORTS', null=True)
    ein = BareField(column_name='EIN', null=True)
    einsubcode = BareField(column_name='EINSUBCODE', null=True)
    elecauditheaderid = BareField(column_name='ELECAUDITHEADERID', null=True)
    entity_type = BareField(column_name='ENTITY_TYPE', null=True)
    facaccepteddate = BareField(column_name='FACACCEPTEDDATE', null=True)
    findingrefnum = BareField(column_name='FINDINGREFNUM', null=True)
    fyenddate = BareField(column_name='FYENDDATE', null=True)
    fystartdate = BareField(column_name='FYSTARTDATE', null=True)
    goingconcern = BareField(column_name='GOINGCONCERN', null=True)
    id = BareField(column_name='ID', null=True)
    image = BareField(column_name='IMAGE', null=True)
    initialdate = BareField(column_name='INITIALDATE', null=True)
    lowrisk = BareField(column_name='LOWRISK', null=True)
    materialnoncompliance = BareField(column_name='MATERIALNONCOMPLIANCE', null=True)
    materialweakness = BareField(column_name='MATERIALWEAKNESS', null=True)
    materialweakness_mp = BareField(column_name='MATERIALWEAKNESS_MP', null=True)
    multipleduns = BareField(column_name='MULTIPLEDUNS', null=True)
    multipleeins = BareField(column_name='MULTIPLEEINS', null=True)
    multipleueis = BareField(column_name='MULTIPLEUEIS', null=True)
    multiple_cpas = BareField(column_name='MULTIPLE_CPAS', null=True)
    #numericmonths = BareField(column_name='NUMERICMONTHS', null=True)
    opeid = BareField(column_name='OPEID', null=True)
    oversightagency = BareField(column_name='OVERSIGHTAGENCY', null=True)
    periodcovered = BareField(column_name='PERIODCOVERED', null=True)
    previousdatefirewall = BareField(column_name='PREVIOUSDATEFIREWALL', null=True)
    pyschedule = BareField(column_name='PYSCHEDULE', null=True)
    qcosts = BareField(column_name='QCOSTS', null=True)
    reportablecondition = BareField(column_name='REPORTABLECONDITION', null=True)
    reportablecondition_mp = BareField(column_name='REPORTABLECONDITION_MP', null=True)
    reportrequired = BareField(column_name='REPORTREQUIRED', null=True)
    sd_materialweakness = BareField(column_name='SD_MATERIALWEAKNESS', null=True)
    sd_materialweakness_mp = BareField(column_name='SD_MATERIALWEAKNESS_MP', null=True)
    significantdeficiency = BareField(column_name='SIGNIFICANTDEFICIENCY', null=True)
    significantdeficiency_mp = BareField(column_name='SIGNIFICANTDEFICIENCY_MP', null=True)
    sp_framework = BareField(column_name='SP_FRAMEWORK', null=True)
    sp_framework_required = BareField(column_name='SP_FRAMEWORK_REQUIRED', null=True)
    state = BareField(column_name='STATE', null=True)
    street1 = BareField(column_name='STREET1', null=True)
    street2 = BareField(column_name='STREET2', null=True)
    suppression_code = BareField(column_name='SUPPRESSION_CODE', null=True)
    totfedexpend = BareField(column_name='TOTFEDEXPEND', null=True)
    typeaudit_code = BareField(column_name='TYPEAUDIT_CODE', null=True)
    typefinding = BareField(column_name='TYPEFINDING', null=True)
    typefunding = BareField(column_name='TYPEFUNDING', null=True)
    typeofentity = BareField(column_name='TYPEOFENTITY', null=True)
    typereport_fs = BareField(column_name='TYPEREPORT_FS', null=True)
    typereport_mp = BareField(column_name='TYPEREPORT_MP', null=True)
    typereport_sp_framework = BareField(column_name='TYPEREPORT_SP_FRAMEWORK', null=True)
    uei = BareField(column_name='UEI', null=True)
    zipcode = BareField(column_name='ZIPCODE', null=True)

    class Meta:
        table_name = 'ELECAUDITHEADER'
        primary_key = False

class Ims(BaseModel):

    audityear = BareField(column_name='AUDITYEAR', null=True)
    dbkey = BareField(column_name='DBKEY', null=True)
    id = BareField(column_name='ID', null=True)
    id2 = BareField(column_name='ID2', null=True)
    image_exists = BareField(column_name='IMAGE_EXISTS', null=True)
    reportid = BareField(column_name='REPORTID', null=True)
    suppression_code = BareField(column_name='SUPPRESSION_CODE', null=True)
    typeaudit_code = BareField(column_name='TYPEAUDIT_CODE', null=True)
    version = IntegerField(column_name='VERSION', null=True)

    class Meta:
        table_name = 'ELECAUDITHEADER_IMS'
        primary_key = False


class Renaming(BaseModel):

    year = TextField()
    id2 = TextField()
    version = TextField()
    census_path = TextField()
    census_name = TextField()
    census_file_exists = IntegerField(null=True)
    gsa_path = TextField()
    gsa_name = TextField()
    gsa_file_copied = IntegerField(null=True)
    
def create_table_from_template(table, db_file):
    if table == "ELECAUDITHEADER_IMS":
        template = ims_table_template
    else:
        template = audit_table_template

    fields = list(template.keys())
    con = sqlite3.connect(db_file)
    cur = con.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS {table}({','.join(fields)})")

def namespace_to_dict(namespace):
    return {
        k: namespace_to_dict(v) if isinstance(v, argparse.Namespace) else v
        for k, v in vars(namespace).items()
    }

def escape(o):
    return "'" + re.sub("'", "''", str(o)) + "'"


def load_table_from_template(table, db_filename, objs):
    conn = sqlite3.connect(db_filename)
    cur = conn.cursor()
    for o in objs:
        keys = ",".join(map(str, list(namespace_to_dict(o).keys())))
        values = ",".join(map(escape, namespace_to_dict(o).values()))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        cur.execute(sql)
    conn.commit()
