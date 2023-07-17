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

class DisseminationFinding(BaseModel):
    id = BigAutoField()
    report_id = CharField()
    award_seq_number = IntegerField(null=True)
    finding_seq_number = IntegerField(null=True)
    finding_ref_number = CharField(index=True)
    prior_finding_ref_numbers = CharField(null=True)
    is_modified_opinion = BooleanField(null=True)
    is_other_matters = BooleanField(null=True)
    is_material_weakness = BooleanField(null=True)
    is_significant_deficiency = BooleanField(null=True)
    is_other_findings = BooleanField(null=True)
    is_questioned_costs = BooleanField(null=True)
    is_repeat_finding = BooleanField(null=True)
    type_requirement = CharField(null=True)

    class Meta:
        table_name = 'dissemination_finding'
        indexes = (
            (('report_id', 'award_seq_number', 'finding_seq_number'), True),
        )

