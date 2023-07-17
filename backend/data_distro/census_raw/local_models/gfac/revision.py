from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'user': 'postgres', 'password': ''})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class DisseminationRevision(BaseModel):
    id = BigAutoField()
    findings = CharField(null=True)
    revision_id = IntegerField(null=True)
    federal_awards = CharField(null=True)
    general_info_explain = TextField(null=True)
    federal_awards_explain = TextField(null=True)
    notes_to_sefa_explain = TextField(null=True)
    audit_info_explain = TextField(null=True)
    findings_explain = TextField(null=True)
    findings_text_explain = TextField(null=True)
    cap_explain = TextField(null=True)
    other_explain = TextField(null=True)
    audit_info = CharField(null=True)
    notes_to_sefa = CharField(null=True)
    findings_text = CharField(null=True)
    cap = CharField(null=True)
    other = CharField(null=True)
    general_info = CharField(null=True)
    audit_year = CharField()
    report_id = CharField()

    class Meta:
        table_name = 'dissemination_revision'

