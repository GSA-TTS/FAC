from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class DisseminationFindingtext(BaseModel):
    id = BigAutoField()
    report_id = CharField()
    finding_ref_number = CharField(null=True)
    charts_tables = BooleanField(null=True)
    finding_text = TextField(null=True)

    class Meta:
        table_name = 'dissemination_findingtext'
        indexes = (
            (('report_id', 'finding_ref_number'), True),
        )

