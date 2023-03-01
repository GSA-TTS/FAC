import json
import logging

from django.apps import apps
from django.core.management.base import BaseCommand

from data_distro.mappings.upload_dictonaries import (
    tables,
    file_to_table_name_mapping,
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    Crates a mapping that can be used by public_data_loader to map data from the downloads
    to the models, using the documentation in the models.

    1) Make sure things like new_fields and table mappings are up to date
    2) Check the outputs to make sure that things make sense.

    You will need to do a manual check on the upload mapping, If a data column needs
    to go to more than one model, that needs to be addressed in the upload script. For
    example, AUDITOR_EIN has the same info reported on two of the upload tables, so you
    only need to upload it once.

    Output will appear in data_distro/mappings/upload_mapping.json

    sample_upload_mapping_structure = {
        "table file name": {
            "column_name": ["model_name", "django_field_name"],
            "column_name2": ["model_name", "django_field_name2"],
        }
    }

    See docs/data_loaing.md for more details.
    """

    def handle(self, *args, **kwargs):
        add_realtional = []
        blank_help = []
        leftovers = []
        # preload tables into a dict
        upload_mapping = {}
        for table_title in tables:
            upload_mapping[table_title] = {}

        new_fields = [
            # django generates
            "id",
            # I added
            "is_public",
            "data_source",
            "create_date",
            "modified_date",
            # relational links. These will change if you move fields around
            "general",
            "findings_text",
        ]

        leftovers = []

        distro_classes = apps.all_models["data_distro"]
        # this should be enough to make a key
        for model in distro_classes:
            mod_class = distro_classes[model]
            mod_name = mod_class.__name__
            fields = mod_class._meta.get_fields()
            for field in fields:
                f_name = field.name
                try:
                    help_text = field.help_text
                except AttributeError:
                    help_text = ""
                    add_realtional.append([f_name, model])
                    new_fields.append(f_name)
                if help_text != "":
                    help_text = field.help_text
                    sources = help_text.split(" (AND) ")
                    for source in sources:
                        cen_source = source.split("Census mapping: ", 1)[1]
                        table_doc_name = cen_source.split(", ", 1)[0]
                        column_name = cen_source.split(", ", 1)[1]
                        table_file_name = file_to_table_name_mapping[
                            table_doc_name.upper().replace(" ", "")
                        ]
                        upload_mapping[table_file_name][column_name] = [
                            mod_name,
                            f_name,
                        ]
                else:
                    if f_name not in new_fields:
                        blank_help.append(f_name)
                    else:
                        # just a check
                        leftovers.append(f_name)

        if len(blank_help) > 0:
            logger.warn(f"~ WARNING ~ Check blank fields: blank_help={blank_help}")

        # this should be relational fields
        logger.warn(
            f"Fields with no help (relational and array models that need some custom logic for loading): add_realtional={add_realtional}"
        )

        logger.warn(f"Data not in mapping: {leftovers}")

        with open("data_distro/mappings/new_upload_mapping.json", "w") as outfile:
            json.dump(upload_mapping, outfile)
