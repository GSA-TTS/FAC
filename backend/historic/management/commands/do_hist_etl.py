from django.core.management.base import BaseCommand
from historic.etl import ETL


class Command(BaseCommand):
    @staticmethod
    def _validate_audit_year(audit_year):
        if audit_year < 2016 or audit_year > 2022:
            raise ValueError("The audit year must be between 2016 and 2022.")

    def add_arguments(self, parser):
        parser.add_argument("audit_year", type=int, help="The audit year to process.")

    def handle(self, *args, **kwargs):
        audit_year = kwargs["audit_year"]

        if not audit_year:
            self.stderr.write("Please specify the audit year as an input argument.")
            return

        try:
            self._validate_audit_year(audit_year)
        except ValueError as e:
            self.stderr.write(str(e))
            self.stderr.write("For help, run `python manage.py help do_hist_etl`.")
            return

        etl = ETL(audit_year=audit_year)
        etl.load_general()
        etl.load_award()
