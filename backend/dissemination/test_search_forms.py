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
