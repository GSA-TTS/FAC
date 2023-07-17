from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'user': 'postgres', 'password': ''})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Eleccpas(BaseModel):
    id = TextField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    seqnum = DecimalField(null=True)
    version = DecimalField(null=True)
    cpafirmname = TextField(null=True)
    cpastreet1 = TextField(null=True)
    cpacity = TextField(null=True)
    cpastate = TextField(null=True)
    cpazipcode = TextField(null=True)
    cpacontact = TextField(null=True)
    cpatitle = TextField(null=True)
    cpaphone = TextField(null=True)
    cpafax = TextField(null=True)
    cpaemail = TextField(null=True)
    cpaein = TextField(null=True)

    class Meta:
        table_name = 'ELECCPAS'
        primary_key = False

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'user': 'postgres', 'password': ''})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Eleccpas(BaseModel):
    id = TextField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    seqnum = DecimalField(null=True)
    version = DecimalField(null=True)
    cpafirmname = TextField(null=True)
    cpastreet1 = TextField(null=True)
    cpacity = TextField(null=True)
    cpastate = TextField(null=True)
    cpazipcode = TextField(null=True)
    cpacontact = TextField(null=True)
    cpatitle = TextField(null=True)
    cpaphone = TextField(null=True)
    cpafax = TextField(null=True)
    cpaemail = TextField(null=True)
    cpaein = TextField(null=True)

    class Meta:
        table_name = 'ELECCPAS'
        primary_key = False

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Eleccpas(BaseModel):
    id = TextField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    seqnum = DecimalField(null=True)
    version = DecimalField(null=True)
    cpafirmname = TextField(null=True)
    cpastreet1 = TextField(null=True)
    cpacity = TextField(null=True)
    cpastate = TextField(null=True)
    cpazipcode = TextField(null=True)
    cpacontact = TextField(null=True)
    cpatitle = TextField(null=True)
    cpaphone = TextField(null=True)
    cpafax = TextField(null=True)
    cpaemail = TextField(null=True)
    cpaein = TextField(null=True)

    class Meta:
        table_name = 'ELECCPAS'
        primary_key = False

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Eleccpas(BaseModel):
    id = TextField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    seqnum = DecimalField(null=True)
    version = DecimalField(null=True)
    cpafirmname = TextField(null=True)
    cpastreet1 = TextField(null=True)
    cpacity = TextField(null=True)
    cpastate = TextField(null=True)
    cpazipcode = TextField(null=True)
    cpacontact = TextField(null=True)
    cpatitle = TextField(null=True)
    cpaphone = TextField(null=True)
    cpafax = TextField(null=True)
    cpaemail = TextField(null=True)
    cpaein = TextField(null=True)

    class Meta:
        table_name = 'ELECCPAS'
        primary_key = False

