from django.core.management.base import BaseCommand, CommandError

from curation.curationlib.flag_disseminated_for_removal import (
    flag_disseminated_for_removal,
)


class Command(BaseCommand):
    help = "Administratively flag a disseminated audit for removal."

    def add_arguments(self, parser):
        parser.add_argument(
            "report_id",
            type=str,
            help="Report ID of the disseminated audit to flag for removal.",
        )
        parser.add_argument(
            "--email",
            required=True,
            help="Email address of the FAC staff user performing the action.",
        )

    def handle(self, *args, **options):
        report_id = options["report_id"]
        email = options["email"]

        try:
            sac = flag_disseminated_for_removal(
                report_id=report_id,
                email=email,
            )
        except (ValueError, RuntimeError) as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully flagged audit {sac.report_id} for removal."
            )
        )
