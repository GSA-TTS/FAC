from django.test import TestCase

from dissemination.forms.search_forms import SearchForm


class SearchFormTests(TestCase):
    def test_uei_or_ein_removes_dashes(self):
        form = SearchForm(data={"uei_or_ein": "12-3456789"})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["uei_or_ein"], ["123456789"])

    def test_uei_or_ein_separates_commas(self):
        form = SearchForm(data={"uei_or_ein": "123456789,987654321"})

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["uei_or_ein"],
            ["123456789", "987654321"],
        )

    def test_uei_or_ein_separates_newlines(self):
        form = SearchForm(data={"uei_or_ein": "123456789\n987654321"})

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["uei_or_ein"],
            ["123456789", "987654321"],
        )

    def test_clean_report_id_z(self):
        """Ensures that report_id_z is parsed and replaces the value of report_id"""
        form = SearchForm(
            data={
                "report_id_z": "eJxVyTEOgDAMA8Cdv1iynaAmY4UED-D_f0Hdyq1nOsHA8857XiBJVbZ5mBY49qloU2sC0j7ZLo01J_ibVnnEGoO9T1Cd9QHLkxrD",
            },
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["report_id"],
            [
                "2024-03-GSAFAC-0000184920",
                "2021-07-GSAFAC-0000839201",
                "2023-11-GSAFAC-0000492817",
                "2025-01-GSAFAC-0000918273",
                "2022-09-GSAFAC-0000301948",
            ],
        )
