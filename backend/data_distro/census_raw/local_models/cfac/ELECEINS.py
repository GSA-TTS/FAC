from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'user': 'postgres', 'password': ''})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Eleceins(BaseModel):
    id = TextField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    ein = TextField(null=True)
    einseqnum = DecimalField(null=True)
    duns = TextField(null=True)
    dunseqnum = DecimalField(null=True)

    class Meta:
        table_name = 'ELECEINS'
        primary_key = False

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'user': 'postgres', 'password': ''})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Eleceins(BaseModel):
    id = TextField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    ein = TextField(null=True)
    einseqnum = DecimalField(null=True)
    duns = TextField(null=True)
    dunseqnum = DecimalField(null=True)

    class Meta:
        table_name = 'ELECEINS'
        primary_key = False

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Eleceins(BaseModel):
    id = TextField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    ein = TextField(null=True)
    einseqnum = DecimalField(null=True)
    duns = TextField(null=True)
    dunseqnum = DecimalField(null=True)

    class Meta:
        table_name = 'ELECEINS'
        primary_key = False

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Eleceins(BaseModel):
    id = TextField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    ein = TextField(null=True)
    einseqnum = DecimalField(null=True)
    duns = TextField(null=True)
    dunseqnum = DecimalField(null=True)

    class Meta:
        table_name = 'ELECEINS'
        primary_key = False

