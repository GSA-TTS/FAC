import os
from django.db import connection
from django.test import TestCase

# Use this TestMaterializedViewBuilder class as a base class for TestCases that
# make use of a materialized view.


class TestMaterializedViewBuilder(TestCase):
    def setUp(self):
        super().setUp()
        self.execute_sql_file("dissemination/sql/create_materialized_views.sql")

    def tearDown(self):
        self.execute_sql_file("dissemination/sql/drop_materialized_views.sql")
        super().tearDown()

    def execute_sql_file(self, relative_path):
        """Execute the SQL commands in the file at the given path."""
        full_path = os.path.join(os.getcwd(), relative_path)
        try:
            with open(full_path, "r") as file:
                sql_commands = file.read()
            with connection.cursor() as cursor:
                cursor.execute(sql_commands)
        except Exception as e:
            print(f"Error executing SQL command: {e}")

    def refresh_materialized_view(self):
        """Refresh the materialized view"""
        self.execute_sql_file("dissemination/sql/refresh_materialized_views.sql")
