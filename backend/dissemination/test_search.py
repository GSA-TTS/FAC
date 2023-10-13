from django.test import TestCase

from dissemination.models import General
from dissemination.search import search_general

from model_bakery import baker

import datetime
import random


class SearchTests(TestCase):
    def test_search_general_empty_query(self):
        """
        Given empty query parameters, search_general should return all records
        """
        generals_count = random.randint(50, 100)
        baker.make(General, _quantity=generals_count)

        results = search_general(
            names=None,
            uei_or_eins=None,
            start_date=None,
            end_date=None,
            cog_or_oversight=None,
            agency_name=None,
        )

        self.assertEqual(len(results), generals_count)

    def test_search_general_date_range(self):
        """
        Given a start and end date, search_general should return only records inside the date range
        """

        # seed the database with one record for each day of June
        seed_start_date = datetime.date(2023, 6, 1)
        seed_end_date = datetime.date(2023, 6, 30)

        d = seed_start_date
        while d <= seed_end_date:
            baker.make(General, fac_accepted_date=d)
            d += datetime.timedelta(days=1)

        # search for records between June 10 and June 15
        search_start_date = datetime.date(2023, 6, 10)
        search_end_date = datetime.date(2023, 6, 15)

        results = search_general(
            names=None,
            uei_or_eins=None,
            start_date=search_start_date,
            end_date=search_end_date,
            cog_or_oversight=None,
            agency_name=None,
        )

        # we should get 6 results, one for each day between June 10-15
        self.assertEqual(len(results), 6)

        for r in results:
            self.assertGreaterEqual(r.fac_accepted_date, search_start_date)
            self.assertLessEqual(r.fac_accepted_date, search_end_date)
