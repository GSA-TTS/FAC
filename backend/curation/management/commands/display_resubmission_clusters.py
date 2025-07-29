from curation.curationlib.generate_resubmission_clusters import (
    generate_resbmission_clusters,
)
from curation.curationlib.export_resubmission_clusters import (
    # export_sets_as_text_tables,
    export_sets_as_csv,
    export_sets_as_markdown,
)

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Clusters audits for resubmission linking"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--audit_year",
            type=str,
            required=True,
            help="Audit year to process",
        )
        parser.add_argument("--noisy", action="store_true")
        parser.add_argument("--quiet", dest="noisy", action="store_false")
        parser.set_defaults(noisy=True)

    def handle(self, *args, **options):
        sorted_sets = generate_resbmission_clusters(
            options["audit_year"], noisy=options["noisy"]
        )

        # export_sets_as_text_tables(
        #     options["audit_year"], sorted_sets, noisy=options["noisy"]
        # )
        export_sets_as_csv(options["audit_year"], sorted_sets, noisy=options["noisy"])
        export_sets_as_markdown(
            options["audit_year"], sorted_sets, noisy=options["noisy"]
        )
