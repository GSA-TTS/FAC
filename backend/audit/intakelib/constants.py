from django.conf import settings

AWARD_ENTITY_NAME_PATH = (
    "FederalAwards.federal_awards.direct_or_indirect_award.entities.passthrough_name"
)
AWARD_ENTITY_ID_PATH = "FederalAwards.federal_awards.direct_or_indirect_award.entities.passthrough_identifying_number"
AWARD_ENTITY_NAME_KEY = "passthrough_name"
AWARD_ENTITY_ID_KEY = "passthrough_identifying_number"
FEDERAL_AGENCY_PREFIX = "federal_agency_prefix"
THREE_DIGIT_EXTENSION = "three_digit_extension"
SECTION_NAME = "section_name"
XLSX_TEMPLATE_DEFINITION_DIR = settings.XLSX_TEMPLATE_JSON_DIR
