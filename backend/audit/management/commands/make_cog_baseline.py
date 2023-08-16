from django.core.management.base import BaseCommand
from audit.cog_over import set_2019_baseline


class Command(BaseCommand):
    help = """
    Populates CognizantBaseline using data in census_gen19 and census_cfda19 .
    """

    def handle(self, *args, **kwargs):
        set_2019_baseline()
