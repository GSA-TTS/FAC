from django.test import TestCase
from collections import defaultdict
import logging

from support.management.commands.seed_cog_baseline import load_cog_2021_2025
from support.models import CognizantBaseline

import pandas as pd
from config.settings import BASE_DIR
from os import path

logger = logging.getLogger(__name__)

TEST_DBKEY = '161024'
TEST_EIN = '566001021'


class SeedCogBaselineTests(TestCase):
    def test_load_empty_cogbaseline_table(self):
        logger.info("test_load_empty_cogbaseline_tab")
        count = load_cog_2021_2025("test_load_census_baseline.csv")
        self.assertEqual(count, 29)

    def test_add_gsa_override_and_inactive_to_cogbaseline_table(self):
        dtypes = defaultdict(lambda: str)
        logger.info("test_add_gsa_override_and_inactive_to_cogbaseline_table")
        file_path = path.join(
            BASE_DIR, "support/fixtures/", "test_load_census_baseline.csv"
        )
        df = pd.read_csv(file_path, dtype=dtypes)
        self.assertEqual(df.shape[0], 29)

        df_sub = df[(df["DBKEY"] == TEST_DBKEY) & (df["EIN"] == TEST_EIN)]
        num_row = df_sub.shape[0]
        self.assertEqual(num_row, 1)
        self.assertEqual(df_sub["COGAGENCY"].values, "10")

        count = load_cog_2021_2025("test_load_census_baseline.csv")
        CognizantBaseline.objects.filter(dbkey=TEST_DBKEY, ein=TEST_EIN).update(
            is_active=False
        )

        file_path = path.join(
            BASE_DIR, "support/fixtures/", "test_load_gsa_override.csv"
        )
        df = pd.read_csv(file_path, dtype=dtypes)
        self.assertEqual(df.shape[0], 31)

        df_sub = df[(df["DBKEY"] == TEST_DBKEY) & (df["EIN"] == TEST_EIN)]
        num_row = df_sub.shape[0]
        self.assertEqual(num_row, 1)
        self.assertEqual(df_sub["COGAGENCY"].values, "18")

        count = load_cog_2021_2025("test_load_gsa_override.csv")

        count = CognizantBaseline.objects.count()
        self.assertEqual(count, 32)

        cogbaseline_row = CognizantBaseline.objects.get(
            dbkey=TEST_DBKEY, ein=TEST_EIN, is_active=True
        )
        self.assertEqual(cogbaseline_row.cognizant_agency, "18")

    def test_gsa_override_reload_to_cogbaseline_table(self):
        logger.info("test_gsa_override_reload_to_cogbaseline_table")
        count = load_cog_2021_2025("test_load_gsa_override.csv")
        count = load_cog_2021_2025("test_load_census_baseline.csv")
        self.assertEqual(count, 29)
