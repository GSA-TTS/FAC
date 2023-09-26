from django.core.management.base import BaseCommand
from django.apps import apps
from audit.models import SingleAuditChecklist
from config import settings


class Command(BaseCommand):
    help = """
    This is a testing utility that should only be used locally and in dev.
    It deletes all data in the postgres database.
    It was build to test backup and restore,
    """

    def handle(self, *args, **kwargs):
        if settings.ENVIRONMENT not in [
            "DEVELOPMENT",
            "LOCAL",
        ]:
            print("This command works only in LOCAL or DEVELOPMENT environments")
        else:
            self.purge_tables()

    def purge_tables(self):
        # Delete SAC first to aboid FK protection issues
        SingleAuditChecklist.objects.all().delete()

        for app in apps.get_app_configs():
            for model in app.get_models():
                model.objects.all().delete()
