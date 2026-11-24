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
                "report_ids_z": "eJxVyTEOgDAMA8Cdv1iynaAmY4UED-D_f0Hdyq1nOsHA8857XiBJVbZ5mBY49qloU2sC0j7ZLo01J_ibVnnEGoO9T1Cd9QHLkxrD",
            },
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["report_ids"],
            [
                "2021-07-GSAFAC-0000839201",
                "2022-09-GSAFAC-0000301948",
                "2023-11-GSAFAC-0000492817",
                "2025-01-GSAFAC-0000918273",
                "2024-03-GSAFAC-0000184920",
            ],
        )

    def test_clean_ueis_and_eins_z(self):
        """Ensures that ueis_and_eins_z is parsed and replaces the value of ueis_and_eins"""
        form = SearchForm(
            data={
                "ueis_and_eins_z": "",
            },
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["ueis_and_eins"],
            [
                "D7A4J33FUMJ1",
                "JWD1G65BD2L5",
                "NEKQDYH9JHN3",
                "NWZLK5MN2YJ6",
                "ZL6YUYB5Z173",
            ],
        )
