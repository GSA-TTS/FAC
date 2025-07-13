from curation.curationlib.generate_resubmission_clusters import (
    generate_clusters_from_records,
)
from curation.curationlib.sac_resubmission_records_postgres import (
    fetch_sac_resubmission_records_postgres,
)

from curation.curationlib.export_resubmission_clusters import (
    export_sets_as_text_tables,
    export_sets_as_csv,
    export_sets_as_markdown,
)

from django.core.management.base import BaseCommand


def generate_resbmission_clusters(AY, noisy=False):
    records = fetch_sac_resubmission_records_postgres(AY, noisy=noisy)
    sorted_sets = generate_clusters_from_records(records, AY, noisy)
    return sorted_sets


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

        export_sets_as_text_tables(
            options["audit_year"], sorted_sets, noisy=options["noisy"]
        )
        export_sets_as_csv(options["audit_year"], sorted_sets, noisy=options["noisy"])
        export_sets_as_markdown(
            options["audit_year"], sorted_sets, noisy=options["noisy"]
        )
