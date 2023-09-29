import csv
import inspect

from psycopg2 import sql
from psycopg2._psycopg import connection

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = """
    Create a csv dictionary in data_distro/mappings/FAC_data_dict.csv.
    Adds column comments to sql.
    """

    def handle(self, *args, **kwargs):
        distro_classes = apps.all_models["data_distro"]
        definations = map_models(distro_classes)
        create_csv(definations)
        create_sql_comments(distro_classes, definations)


def map_models(distro_classes):
    definations = []
    for model in distro_classes:
        mod_class = distro_classes[model]
        mod_name = mod_class.__name__
        fields = mod_class._meta.get_fields()
        for fac_field in fields:
            field_name = fac_field.name
            try:
                help_text = fac_field.help_text
            except AttributeError:
                help_text = None

            try:
                verbose_name = fac_field.verbose_name
            except AttributeError:
                verbose_name = None

            try:
                max_len = str(fac_field.max_length)
            except AttributeError:
                max_len = None
            if max_len not in [None, "None"]:
                field_type = str(fac_field.get_internal_type()) + " Limit: " + max_len
            else:
                field_type = fac_field.get_internal_type()

            field_def = {
                "Model name": mod_name,
                "Field name": field_name,
                "Description": verbose_name,
                "Data Source": help_text,
                "Validation": field_type,
            }
            definations.append(field_def)

    return definations


def create_csv(definations):
    with open("data_distro/mappings/FAC_data_dict.csv", "w", newline="") as csvfile:
        fieldnames = [
            "Model name",
            "Field name",
            "Description",
            "Data Source",
            "Validation",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for line in definations:
            writer.writerow(line)


def create_sql_comments(distro_classes, definations):
    if settings.ENVIRONMENT not in ["DEVELOPMENT", "PREVIEW", "STAGING", "PRODUCTION"]:
        conn_string = "dbname='postgres' user='postgres' port='5432' host='db'"
    else:
        conn_string = settings.CONNECTION_STRING

    api_views = {
        "Auditee": "api.vw_auditee",
        "Auditor": "api.vw_auditor",
        "CapText": "api.vw_cap_text",
        "FederalAward": "api.vw_federal_award",
        "Finding": "api.vw_findings",
        "FindingText": "api.vw_findings_text",
        "General": "api.vw_general",
        "Note": "api.vw_note",
        "Passthrough": "api.vw_passthrough",
        "Revision": "api.vw_revision",
    }

    # Add docs to tables and views
    for model in distro_classes:
        mod_class = distro_classes[model]
        model_name = mod_class.__name__
        doc = inspect.getdoc(mod_class)

        conn = connection(conn_string)
        conn.autocommit = True
        with conn.cursor() as curs:
            curs.execute(
                sql.SQL("COMMENT ON TABLE {} is %s;").format(
                    sql.Identifier("data_distro_{0}".format(model_name.lower())),
                ),
                (doc,),
            )
            if model_name in api_views:
                view = api_views[model_name]
                curs.execute(
                    sql.SQL("COMMENT ON VIEW {} is %s;".format(view)),
                    (doc,),
                )

    # Add docs to fields
    for define_txt in definations:
        model_name = define_txt["Model name"]
        if define_txt["Description"] is not None:
            field_type = define_txt["Validation"]
            if field_type not in ["ForeignKey", "ManyToManyField"]:
                full_defination = str(define_txt["Description"])
                if define_txt["Data Source"] is not None:
                    full_defination = "   ".join(
                        [
                            full_defination,
                            str(define_txt["Data Source"]),
                        ]
                    )
                # add def to table
                conn = connection(conn_string)
                conn.autocommit = True
                with conn.cursor() as curs:
                    curs.execute(
                        # These should be safe strings, but I am going to treat them with caution anyway.
                        sql.SQL("COMMENT ON COLUMN {}.{} is %s;").format(
                            sql.Identifier(
                                "data_distro_{0}".format(model_name.lower())
                            ),
                            sql.Identifier(define_txt["Field name"]),
                        ),
                        (full_defination,),
                    )
                # add def to view
                if model_name in api_views:
                    view = api_views[model_name]
                    conn = connection(conn_string)
                    conn.autocommit = True
                    with conn.cursor() as curs:
                        curs.execute(
                            # These should be safe strings, but I am going to treat them with caution anyway.
                            sql.SQL("COMMENT ON COLUMN {}.{} is %s;").format(
                                sql.SQL(view),
                                sql.Identifier(define_txt["Field name"]),
                            ),
                            (full_defination,),
                        )
