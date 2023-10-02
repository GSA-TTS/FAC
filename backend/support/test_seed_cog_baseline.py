from django.test import TestCase
import logging

from support.management.commands.seed_cog_baseline import load_cog_2021_2025
from support.models import CognizantBaseline

import pandas as pd
from config.settings import BASE_DIR
from os import path

logger = logging.getLogger(__name__)
from collections import defaultdict


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

        df_sub = df[(df["DBKEY"] == "161024") & (df["EIN"] == "566001021")]
        num_row = df_sub.shape[0]
        self.assertEqual(num_row, 1)

        count = load_cog_2021_2025("test_load_census_baseline.csv")
        CognizantBaseline.objects.filter(dbkey="161024", ein="566001021").update(
            is_active=False
        )

        file_path = path.join(
            BASE_DIR, "support/fixtures/", "test_load_gsa_override.csv"
        )
        df = pd.read_csv(file_path, dtype=dtypes)
        self.assertEqual(df.shape[0], 31)

        count = load_cog_2021_2025("test_load_gsa_override.csv")

        count = CognizantBaseline.objects.count()
        self.assertEqual(count, 32)

    def test_gsa_override_reload_to_cogbaseline_table(self):
        logger.info("test_gsa_override_reload_to_cogbaseline_table")
        count = load_cog_2021_2025("test_load_gsa_override.csv")
        count = load_cog_2021_2025("test_load_census_baseline.csv")
        self.assertEqual(count, 29)
