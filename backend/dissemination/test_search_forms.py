from django.test import TestCase

from dissemination.forms.search_forms import SearchForm


class SearchFormTests(TestCase):
    def test_ueis_and_eins_removes_dashes(self):
        form = SearchForm(data={"ueis_and_eins": "12-3456789"})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["ueis_and_eins"], ["123456789"])

    def test_ueis_and_eins_separates_commas(self):
        form = SearchForm(data={"ueis_and_eins": "123456789,987654321"})

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["ueis_and_eins"],
            ["123456789", "987654321"],
        )

    def test_ueis_and_eins_separates_newlines(self):
        form = SearchForm(data={"ueis_and_eins": "123456789\n987654321"})

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["ueis_and_eins"],
            ["123456789", "987654321"],
        )

    def test_clean_report_ids_z(self):
        """Ensures that report_ids_z is parsed and replaces the value of report_ids"""
        form = SearchForm(
            data={
                "report_ids_z": "eJxVyzEOgDAMA8Cdv1iynaAmY4UED-D_f0Hdynw60wIHnnfe8wJJVrSpw7TB3iWozloSkHbJdmksSTB2UWWbS07wd1rlER_MlxrD",
            },
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["report_ids"],
            [
                "2021-07-GSAFAC-0000839201",
                "2022-09-GSAFAC-0000301948",
                "2023-11-GSAFAC-0000492817",
                "2024-03-GSAFAC-0000184920",
                "2025-01-GSAFAC-0000918273",
            ],
        )

    def test_clean_ueis_and_eins_z(self):
        """Ensures that ueis_and_eins_z is parsed and replaces the value of ueis_and_eins"""
        form = SearchForm(
            data={
                "ueis_and_eins_z": "eJwFwUkOwyAMAMC7f0PMohzDagG2SrMV_v-QzpzPktXlbpIVUOMkU_yVgwZ5V2-GZZvVQhi2n6PqUSrC6nbe05ulHALZ14_06MDkILpDV8R8c1UgqY04aa8kCFGSDsKmNLRQs_D87sdvNoT6RlWs8XHrBoieyLG06xcNMH34dS71kfEPnSwrow",
            },
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["ueis_and_eins"],
            [
                "CQ6LSQJ4QGJ3",
                "D7A4J33FUMJ1",
                "DNE4CNM5GK36",
                "H6WBQEV4CMH7",
                "HHVDMDGKTXD5",
                "HKMENYNBTFC4",
                "JFNMYR9AXYK3",
                "JWD1G65BD2L5",
                "MHPMW77ELQF3",
                "NEKQDYH9JHN3",
                "NWZLK5MN2YJ6",
                "SVZNZLNUKNF1",
                "ZL6YUYB5Z173",
            ],
        )
