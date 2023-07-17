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

class DisseminationGenauditor(BaseModel):
    id = BigAutoField()
    report_id = CharField()
    auditor_seq_number = IntegerField()
    auditor_city = CharField(null=True)
    auditor_contact_title = CharField(null=True)
    auditor_country = CharField(null=True)
    auditor_ein = IntegerField(null=True)
    auditor_email = CharField(null=True)
    auditor_phone = BigIntegerField(null=True)
    auditor_state = CharField(null=True)
    auditor_address_line_1 = CharField(null=True)
    auditor_zip = CharField(null=True)
    auditor_firm_name = CharField()
    auditor_foreign_addr = CharField(null=True)

    class Meta:
        table_name = 'dissemination_genauditor'
        indexes = (
            (('report_id', 'auditor_seq_number'), True),
        )

