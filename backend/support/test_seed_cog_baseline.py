from django.test import TestCase

from support.management.commands.seed_cog_baseline import load_cog_2021_2025
from support.models import CognizantBaseline


class SeedCogBaselineTests(TestCase):
    def test_load_empty_cogbaseline_table(self):
        print("Start SeedCogBaseline Test #1")
        count = load_cog_2021_2025("test_load_census_baseline.csv")
        self.assertEqual(count, 29)
        print("End SeedCogBaseline Test #1")

    def test_add_gsa_override_and_inactive_to_cogbaseline_table(self):
        print("Start SeedCogBaseline Test #2")
        count = load_cog_2021_2025("test_load_census_baseline.csv")
        CognizantBaseline.objects.filter(dbkey="161024", ein="566001021").update(
            is_active=False
        )
        count = load_cog_2021_2025("test_load_gsa_override.csv")
        count = CognizantBaseline.objects.count()
        self.assertEqual(count, 32)
        print("End SeedCogBaseline Test #2")

    def test_gsa_override_reload_to_cogbaseline_table(self):
        print("Start SeedCogBaseline Test #3")
        count = load_cog_2021_2025("test_load_gsa_override.csv")
        count = load_cog_2021_2025("test_load_census_baseline.csv")
        self.assertEqual(count, 29)
        print("End SeedCogBaseline Test #3")
