from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Elecauditfindings(BaseModel):
    elecauditfindingsid = DecimalField(null=True)
    qcosts = TextField(null=True)
    otherfindings = TextField(null=True)
    significantdeficiency = TextField(null=True)
    materialweakness = TextField(null=True)
    othernoncompliance = TextField(null=True)
    typerequirement = TextField(null=True)
    findingrefnums = TextField(null=True)
    reportid = DecimalField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    version = DecimalField(null=True)
    elecauditsid = DecimalField(null=True)
    modifiedopinion = TextField(null=True)
    repeatfinding = TextField(null=True)
    priorfindingrefnums = TextField(null=True)

    class Meta:
        table_name = 'ELECAUDITFINDINGS'
        primary_key = False

