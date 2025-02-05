import logging

from django.core.management.base import BaseCommand

from dissemination.models import General

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = """
    One time script to migrate existing dissemination tables into the new audit table.
    """

    def handle(self, *args, **kwargs):
        general = General.objects.first()

        return
