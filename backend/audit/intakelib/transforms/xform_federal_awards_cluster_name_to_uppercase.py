import logging
from audit.intakelib.common import make_named_range_uppercase

logger = logging.getLogger(__name__)


# DESCRIPTION
# Convert federal_awards cluster_name to uppercase.
def convert_federal_awards_cluster_name_to_uppercase(ir):
    return make_named_range_uppercase(ir, "cluster_name", "check_cluster_names")
