from django.test import TestCase

from support.management.commands.seed_cog_baseline import load_cog_2021_2025
from support.models import CognizantBaseline

import pandas as pd
from config.settings import BASE_DIR
from os import path


class SeedCogBaselineTests(TestCase):
    def test_load_empty_cogbaseline_table(self):
        count = load_cog_2021_2025("test_load_census_baseline.csv")
        self.assertEqual(count, 29)

    def test_add_gsa_override_and_inactive_to_cogbaseline_table(self):
        file_path = path.join(
            BASE_DIR, "support/fixtures/", "test_load_census_baseline.csv"
        )
        df = pd.read_csv(file_path)
        self.assertEqual(df.shape[0], 29)

        count = load_cog_2021_2025("test_load_census_baseline.csv")
        CognizantBaseline.objects.filter(dbkey="161024", ein="566001021").update(
            is_active=False
        )

        file_path = path.join(
            BASE_DIR, "support/fixtures/", "test_load_gsa_override.csv"
        )
        df = pd.read_csv(file_path)
        self.assertEqual(df.shape[0], 31)

        count = load_cog_2021_2025("test_load_gsa_override.csv")

        count = CognizantBaseline.objects.count()
        self.assertEqual(count, 32)

    def test_gsa_override_reload_to_cogbaseline_table(self):
        count = load_cog_2021_2025("test_load_gsa_override.csv")
        count = load_cog_2021_2025("test_load_census_baseline.csv")
        self.assertEqual(count, 29)
