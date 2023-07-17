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

class DisseminationFederalaward(BaseModel):
    id = BigAutoField()
    report_id = CharField()
    award_seq_number = IntegerField()
    federal_agency_prefix = CharField()
    federal_award_extension = CharField()
    additional_award_identification = CharField(null=True)
    federal_program_name = CharField(null=True)
    amount_expended = BigIntegerField()
    cluster_name = CharField(null=True)
    other_cluster_name = CharField(null=True)
    state_cluster_name = CharField(null=True)
    cluster_total = BigIntegerField(null=True)
    federal_program_total = BigIntegerField(null=True)
    is_loan = BooleanField(null=True)
    loan_balance = BigIntegerField(null=True)
    is_direct = BooleanField(null=True)
    is_major = BooleanField(null=True)
    mp_audit_report_type = CharField(null=True)
    findings_count = IntegerField(null=True)
    is_passthrough_award = BooleanField(null=True)
    passthrough_name = TextField(null=True)
    passthrough_id = TextField(null=True)
    passthrough_amount = BigIntegerField(null=True)
    type_requirement = CharField(null=True)

    class Meta:
        table_name = 'dissemination_federalaward'
        indexes = (
            (('report_id', 'award_seq_number'), True),
        )

