from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'user': 'postgres', 'password': ''})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Elecnotes(BaseModel):
    id = DecimalField(null=True)
    reportid = DecimalField(null=True)
    version = DecimalField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    seq_number = DecimalField(null=True)
    type_id = DecimalField(null=True)
    note_index = DecimalField(null=True)
    title = TextField(null=True)
    content = TextField(null=True)
    uei = TextField(null=True)
    multipleueis = TextField(null=True)

    class Meta:
        table_name = 'ELECNOTES'
        primary_key = False

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'user': 'postgres', 'password': ''})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Elecnotes(BaseModel):
    id = DecimalField(null=True)
    reportid = DecimalField(null=True)
    version = DecimalField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    seq_number = DecimalField(null=True)
    type_id = DecimalField(null=True)
    note_index = DecimalField(null=True)
    title = TextField(null=True)
    content = TextField(null=True)
    uei = TextField(null=True)
    multipleueis = TextField(null=True)

    class Meta:
        table_name = 'ELECNOTES'
        primary_key = False

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Elecnotes(BaseModel):
    id = DecimalField(null=True)
    reportid = DecimalField(null=True)
    version = DecimalField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    seq_number = DecimalField(null=True)
    type_id = DecimalField(null=True)
    note_index = DecimalField(null=True)
    title = TextField(null=True)
    content = TextField(null=True)
    uei = TextField(null=True)
    multipleueis = TextField(null=True)

    class Meta:
        table_name = 'ELECNOTES'
        primary_key = False

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Elecnotes(BaseModel):
    id = DecimalField(null=True)
    reportid = DecimalField(null=True)
    version = DecimalField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    seq_number = DecimalField(null=True)
    type_id = DecimalField(null=True)
    note_index = DecimalField(null=True)
    title = TextField(null=True)
    content = TextField(null=True)
    uei = TextField(null=True)
    multipleueis = TextField(null=True)

    class Meta:
        table_name = 'ELECNOTES'
        primary_key = False

