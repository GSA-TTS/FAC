from historic.db import DB
import historic.base as base
from historic.mappings import (
    auditfindings,
    federalaward,
    general,
)
import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


report_id_to_dbkey = {}


def q_select_general(table, year=2021, entity_type='State'):
    return ' '.join([f'SELECT * FROM "{table}"',
                     f'WHERE audityear=\'{year}\'',
                     f'AND entity_type=\'{entity_type}\''
                     ])


def q_select_finding(table, dbkey, audityear):
    return ' '.join([f'SELECT * FROM "{table}"',
                     f'WHERE (audityear = \'{audityear}\')',
                     f'AND (dbkey = {dbkey})'
                     ])

def q_select_dbkeys_in_year(table, dbkeys, year):
    keys = ','.join(dbkeys)
    # print(f'keys: {keys}')
    return ' '.join([f'SELECT * FROM "{table}"',
                     f'WHERE audityear = \'{year}\'',
                     f'AND dbkey in ({keys})'])


def add_report_id(df, ndx):
    return base.next_report_id(df.at[ndx, 'audit_year'],
                               df.at[ndx, 'fac_accepted_date']
                               )

def migrate_general(year, is_public_only):
    database = DB()
    database.read_sql_to_df(q_select_general(
        "ELECAUDITHEADER", year=2021, entity_type='State'))
    database.apply_mappings(general.cfac_to_gfac)
    database.add_column('report_id', add_report_id)
    database.add_column('data_source', lambda df, ndx: "Census")
    database.write_df_to_sql('dissemination_general')
    return database

def build_reportid_map(gen_db : DB):
    the_map = {}
    for dbkey, rid in list(zip(gen_db.df.dbkey, 
                            gen_db.df.report_id)): 
        # print(f'mapping [{int(dbkey)} <- {rid}]')
        the_map[int(dbkey)] = rid
    # print(f'---\nkeys: {the_map.keys()}')
    return the_map

# We assume we're already filtered to a single audit year
def add_rid(the_map):
    def _add_rid(df, ndx):
        dbkey = df.at[ndx, 'dbkey']
        # print(f'looking up mapping [{int(dbkey)}] <- {the_map[int(dbkey)]}')
        return the_map[int(dbkey)]
    return _add_rid

def common_migration(in_db, out_db, year, gen_db, mapping):
    dbkeys = list(gen_db.df.dbkey)
    f_db = DB()
    q = q_select_dbkeys_in_year(in_db, dbkeys, year)
    # print(q)
    f_db.read_sql_to_df(q)
    f_db.apply_mappings(mapping.cfac_to_gfac)
    the_map = build_reportid_map(gen_db)
    f_db.add_column('report_id', add_rid(the_map))
    #print(f_db.df.columns)
    f_db.apply_mappings(mapping.cfac_to_gfac, when='late')
    #print(f_db.df.columns)
    f_db.write_df_to_sql(out_db)
    f_db.close()


def migrate_federalawards(gen_db : DB, year):
    common_migration("ELECAUDITS", 
                     "dissemination_federalaward",
                    year,
                    gen_db,
                    federalaward)

def migrate_auditfindings(gen_db : DB, year):
    common_migration("ELECAUDITFINDINGS", 
                     "dissemination_finding",
                    year,
                    gen_db,
                    auditfindings)

class Command(BaseCommand):
    help = """
    Migrate historical data.
    """

    def add_arguments(self, parser):
        parser.add_argument("--table", type=str, required=False)
        parser.add_argument("--year", type=int, default=2021, required=False)
        parser.add_argument("--is_public_only", type=bool,
                            default=True, required=False)

    def handle(self, *args, **kwargs):
        gen_db = migrate_general(kwargs["year"], kwargs["is_public_only"])
        print("Mapped and transfered general table.")
        migrate_federalawards(gen_db, kwargs["year"])
        print("Mapped and transferred federal awards table.")
        migrate_auditfindings(gen_db, kwargs["year"])
        print("Mapped and transferred audit findings table.")
