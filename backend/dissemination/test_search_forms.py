from django.test import TestCase

from dissemination.forms.search_forms import AdvancedSearchForm, SearchForm


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


class AdvancedSearchFormTests(TestCase):
    def test_uei_or_ein_removes_dashes(self):
        form = AdvancedSearchForm(data={"uei_or_ein": "12-3456789"})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["uei_or_ein"], ["123456789"])

    def test_uei_or_ein_separates_commas(self):
        form = AdvancedSearchForm(data={"uei_or_ein": "123456789,987654321"})

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["uei_or_ein"],
            ["123456789", "987654321"],
        )

    def test_uei_or_ein_separates_newlines(self):
        form = AdvancedSearchForm(data={"uei_or_ein": "123456789\n987654321"})

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["uei_or_ein"],
            ["123456789", "987654321"],
        )
