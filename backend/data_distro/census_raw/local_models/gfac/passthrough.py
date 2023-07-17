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

class DisseminationPassthrough(BaseModel):
    id = BigAutoField()
    report_id = CharField()
    award_seq_number = IntegerField(null=True)
    passthrough_id = CharField(null=True)
    passthrough_name = CharField(null=True)

    class Meta:
        table_name = 'dissemination_passthrough'
        indexes = (
            (('report_id', 'award_seq_number', 'passthrough_id'), True),
        )

