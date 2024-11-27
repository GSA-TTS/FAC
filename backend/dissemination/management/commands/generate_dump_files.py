import json
from collections import namedtuple as NT

from django.core.management.base import BaseCommand
from dissemination.models import (
    General,
    FederalAward,
    Finding,
    FindingText,
    AdditionalUei,
    AdditionalEin,
    CapText,
    Note,
    Passthrough,
    SecondaryAuditor,
)

from django.forms import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model

Table = NT("Table", "model,name,is_public_table")
# Exclude General here.
TABLES_TO_DUMP = [
    # Public tables
    Table(FederalAward, "federal_awards", True),
    Table(Finding, "findings", True),
    Table(Passthrough, "passthroughs", True),
    Table(AdditionalUei, "additional_ueis", True),
    Table(AdditionalEin, "additional_eins", True),
    Table(SecondaryAuditor, "secondary_auditors", True),
    # Suppressed tables
    Table(FindingText, "findings_text", False),
    Table(CapText, "corrective_action_plan_text", False),
    Table(Note, "notes_to_sefa", False),
]


# https://stackoverflow.com/questions/757022/how-do-you-serialize-a-model-instance-in-django
class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Model):
            d = model_to_dict(o)
            if "id" in d:
                del d["id"]
            return d
        return super().default(o)


def dump_general(audit_year):
    public_report_ids = []
    private_report_ids = []
    objs = General.objects.filter(audit_year=audit_year)
    with open(f"{audit_year}-general.json", "w") as fp:
        fp.write("[")
        first = True
        for o in objs:
            if o.is_public:
                public_report_ids.append(o.report_id)
            else:
                private_report_ids.append(o.report_id)
            if first:
                fp.write("\n")
                first = False
            else:
                fp.write(",\n")
            fp.write("\t")
            fp.write(json.dumps(o, cls=ExtendedEncoder))
        fp.write("\n]\n")
    fp.close()
    return (public_report_ids, private_report_ids)


def dump_table(table, audit_year, report_ids):
    with open(f"{audit_year}-{table.name}.json", "w") as fp:
        fp.write("[")
        first = True
        for rid in report_ids:
            objs = table.model.objects.filter(report_id=rid)
            for o in objs:
                if first:
                    fp.write("\n")
                    first = False
                else:
                    fp.write(",\n")
                fp.write("\t")
                fp.write(json.dumps(o, cls=ExtendedEncoder))
        fp.write("\n]\n")
        fp.close()


class Command(BaseCommand):
    help = """
    Runs sql scripts  to recreate access tables for the postgrest API.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-y", "--year", choices=[f"20{x}" for x in range(16, 24)], default=False
        )

    def handle(self, *args, **options):
        audit_year = options["year"]
        (public_report_ids, private_report_ids) = dump_general(audit_year)
        for table in TABLES_TO_DUMP:
            # If it is a public table, dump everything.
            # If it is not a public table, then we only dump
            # the report IDs that were marked is_public=True
            if table.is_public_table:
                dump_table(table, audit_year, public_report_ids + private_report_ids)
            else:
                dump_table(table, audit_year, public_report_ids)
