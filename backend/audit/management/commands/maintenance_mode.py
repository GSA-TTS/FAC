from config import middleware
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for switching "Maintenance Mode".
    When switched on, the entire site and requests will feed through
    /config/middleware.py.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--on",
            action="store_true",
            help="Activates maintenance mode, which disables user access.",
        )
        parser.add_argument(
            "--off",
            action="store_true",
            help="Deactivates maintenance mode, which re-enables user access.",
        )

    def handle(self, *args, **options):

        # NOTE - This goes to NewRelic. Tweak the logs to be a little more clear.
        # I.E., "MAINTENANCE_MODE ON"
        logger.info(
            f"Starting switch... Maintenance mode is currently set to {middleware.is_maintenance_on()}."
        )
        if options.get("off"):
            middleware.change_maintenance(False)
            logger.info(
                "Maintenance mode has been set to False. The application is now open to all users."
            )
        elif options.get("on"):
            middleware.change_maintenance(True)
            logger.info(
                "Maintenance mode has been set to True. The application is now closed off to all users."
            )
        else:
            logger.error(
                "Invalid syntax. Please enter this command with --on or --off."
            )
