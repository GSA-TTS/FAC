from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'user': 'postgres', 'password': ''})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Elecfindingstext(BaseModel):
    seq_number = DecimalField(null=True)
    reportid = DecimalField(null=True)
    version = DecimalField(null=True)
    dbkey = DecimalField(null=True)
    audityear = TextField(null=True)
    findingrefnums = TextField(null=True)
    text = TextField(null=True)
    chartstables = TextField(null=True)
    uei = TextField(null=True)
    multipleueis = TextField(null=True)

    class Meta:
        table_name = 'ELECFINDINGSTEXT'
        primary_key = False
