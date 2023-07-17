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

class DisseminationNote(BaseModel):
    id = BigAutoField()
    report_id = CharField()
    note_seq_number = IntegerField()
    type_id = CharField()
    note_index = IntegerField(null=True)
    content = TextField(null=True)
    note_title = CharField(null=True)

    class Meta:
        table_name = 'dissemination_note'
        indexes = (
            (('report_id', 'note_seq_number'), True),
        )

