from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'user': 'postgres', 'password': ''})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Elecaudits(BaseModel):
    id = TextField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    cfdaseqnum = TextField(null=True)
    cfda = TextField(null=True)
    federalprogramname = TextField(null=True)
    amount = DecimalField(null=True)
    majorprogram = TextField(null=True)
    typerequirement = TextField(null=True)
    qcosts2 = TextField(null=True)
    findings = TextField(null=True)
    findingrefnums = TextField(null=True)
    rd = TextField(null=True)
    direct = TextField(null=True)
    cfda_prefix = TextField(null=True)
    cfda_ext = TextField(null=True)
    ein = TextField(null=True)
    cfda2 = TextField(null=True)
    typereport_mp = TextField(null=True)
    typereport_mp_override = TextField(null=True)
    arra = TextField(null=True)
    loans = TextField(null=True)
    elecauditsid = TextField(null=True)
    findingscount = DecimalField(null=True)
    loanbalance = DecimalField(null=True)
    passthroughamount = DecimalField(null=True)
    awardidentification = TextField(null=True)
    clustername = TextField(null=True)
    passthroughaward = TextField(null=True)
    stateclustername = TextField(null=True)
    programtotal = DecimalField(null=True)
    clustertotal = DecimalField(null=True)
    otherclustername = TextField(null=True)
    cfdaprogramname = TextField(null=True)
    uei = TextField(null=True)
    multipleueis = TextField(null=True)

    class Meta:
        table_name = 'ELECAUDITS'
        primary_key = False

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'user': 'postgres', 'password': ''})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Elecaudits(BaseModel):
    id = TextField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    cfdaseqnum = TextField(null=True)
    cfda = TextField(null=True)
    federalprogramname = TextField(null=True)
    amount = DecimalField(null=True)
    majorprogram = TextField(null=True)
    typerequirement = TextField(null=True)
    qcosts2 = TextField(null=True)
    findings = TextField(null=True)
    findingrefnums = TextField(null=True)
    rd = TextField(null=True)
    direct = TextField(null=True)
    cfda_prefix = TextField(null=True)
    cfda_ext = TextField(null=True)
    ein = TextField(null=True)
    cfda2 = TextField(null=True)
    typereport_mp = TextField(null=True)
    typereport_mp_override = TextField(null=True)
    arra = TextField(null=True)
    loans = TextField(null=True)
    elecauditsid = TextField(null=True)
    findingscount = DecimalField(null=True)
    loanbalance = DecimalField(null=True)
    passthroughamount = DecimalField(null=True)
    awardidentification = TextField(null=True)
    clustername = TextField(null=True)
    passthroughaward = TextField(null=True)
    stateclustername = TextField(null=True)
    programtotal = DecimalField(null=True)
    clustertotal = DecimalField(null=True)
    otherclustername = TextField(null=True)
    cfdaprogramname = TextField(null=True)
    uei = TextField(null=True)
    multipleueis = TextField(null=True)

    class Meta:
        table_name = 'ELECAUDITS'
        primary_key = False

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Elecaudits(BaseModel):
    id = TextField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    cfdaseqnum = TextField(null=True)
    cfda = TextField(null=True)
    federalprogramname = TextField(null=True)
    amount = DecimalField(null=True)
    majorprogram = TextField(null=True)
    typerequirement = TextField(null=True)
    qcosts2 = TextField(null=True)
    findings = TextField(null=True)
    findingrefnums = TextField(null=True)
    rd = TextField(null=True)
    direct = TextField(null=True)
    cfda_prefix = TextField(null=True)
    cfda_ext = TextField(null=True)
    ein = TextField(null=True)
    cfda2 = TextField(null=True)
    typereport_mp = TextField(null=True)
    typereport_mp_override = TextField(null=True)
    arra = TextField(null=True)
    loans = TextField(null=True)
    elecauditsid = TextField(null=True)
    findingscount = DecimalField(null=True)
    loanbalance = DecimalField(null=True)
    passthroughamount = DecimalField(null=True)
    awardidentification = TextField(null=True)
    clustername = TextField(null=True)
    passthroughaward = TextField(null=True)
    stateclustername = TextField(null=True)
    programtotal = DecimalField(null=True)
    clustertotal = DecimalField(null=True)
    otherclustername = TextField(null=True)
    cfdaprogramname = TextField(null=True)
    uei = TextField(null=True)
    multipleueis = TextField(null=True)

    class Meta:
        table_name = 'ELECAUDITS'
        primary_key = False

from peewee import *

database = PostgresqlDatabase('postgres', **{'host': 'localhost', 'port': 5432, 'user': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Elecaudits(BaseModel):
    id = TextField(null=True)
    audityear = TextField(null=True)
    dbkey = DecimalField(null=True)
    cfdaseqnum = TextField(null=True)
    cfda = TextField(null=True)
    federalprogramname = TextField(null=True)
    amount = DecimalField(null=True)
    majorprogram = TextField(null=True)
    typerequirement = TextField(null=True)
    qcosts2 = TextField(null=True)
    findings = TextField(null=True)
    findingrefnums = TextField(null=True)
    rd = TextField(null=True)
    direct = TextField(null=True)
    cfda_prefix = TextField(null=True)
    cfda_ext = TextField(null=True)
    ein = TextField(null=True)
    cfda2 = TextField(null=True)
    typereport_mp = TextField(null=True)
    typereport_mp_override = TextField(null=True)
    arra = TextField(null=True)
    loans = TextField(null=True)
    elecauditsid = TextField(null=True)
    findingscount = DecimalField(null=True)
    loanbalance = DecimalField(null=True)
    passthroughamount = DecimalField(null=True)
    awardidentification = TextField(null=True)
    clustername = TextField(null=True)
    passthroughaward = TextField(null=True)
    stateclustername = TextField(null=True)
    programtotal = DecimalField(null=True)
    clustertotal = DecimalField(null=True)
    otherclustername = TextField(null=True)
    cfdaprogramname = TextField(null=True)
    uei = TextField(null=True)
    multipleueis = TextField(null=True)

    class Meta:
        table_name = 'ELECAUDITS'
        primary_key = False

