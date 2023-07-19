from historic.db import DB
import historic.base as base
from historic.mappings import (
    general,
    federalaward
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
        df['report_id'] = the_map[int(dbkey)]
    return _add_rid

def migrate_auditfindings(gen_db : DB, year):
    dbkeys = list(gen_db.df.dbkey)
    f_db = DB()
    q = q_select_dbkeys_in_year("ELECAUDITS", dbkeys, year)
    # print(q)
    f_db.read_sql_to_df(q)
    f_db.apply_mappings(federalaward.cfac_to_gfac)
    the_map = build_reportid_map(gen_db)
    f_db.add_column('report_id', add_rid(the_map))
    print(f_db.df.columns)
    f_db.apply_mappings(federalaward.cfac_to_gfac, when='late')
    print(f_db.df.columns)
    f_db.write_df_to_sql('dissemination_federalaward')
    f_db.close()


def migrate_auditfindings_slow(gen_db : DB):
    for ndx, (dbkey, audityear, rid) in enumerate(list(zip(gen_db.df.dbkey, 
                                                      gen_db.df.audit_year,
                                                      gen_db.df.report_id))):
        f_db = DB()
        f_db.read_sql_to_df(q_select_finding(
        "ELECAUDITS", dbkey, audityear))
        f_db.apply_mappings(federalaward.cfac_to_gfac)
        print(f"[{ndx:05}] Mapping {dbkey}, {audityear}, {len(f_db.df)}")
        f_db.add_column('report_id', lambda df, ndx: rid)
        # Recreate the table first time through
        mode = None
        if ndx == 0:
            mode = 'replace'
        else:
            mode = 'append'
        f_db.write_df_to_sql('dissemination_federalaward', mode=mode)
        f_db.close()
    

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
        migrate_auditfindings(gen_db, kwargs["year"])
