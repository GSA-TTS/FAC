from django.core.management.base import BaseCommand, CommandError

from curation.curationlib.suppress_audits import suppress_audit


class Command(BaseCommand):
    help = "Administratively suppress a disseminated audit."

    def add_arguments(self, parser):
        parser.add_argument(
            "report_id",
            type=str,
            help="Report ID of the audit to suppress.",
        )
        parser.add_argument(
            "--email",
            required=True,
            help="Email address of the FAC staff user performing the suppression.",
        )

    def handle(self, *args, **options):
        report_id = options["report_id"]
        email = options["email"]

        try:
            sac = suppress_audit(
                report_id=report_id,
                email=email,
            )
        except (ValueError, RuntimeError) as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(f"Successfully suppressed audit {sac.report_id}.")
        )
