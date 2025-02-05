from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """
    One time script to migrate existing dissemination tables into the new audit table.
    """

    def handle(self, *args, **kwargs):
        return
