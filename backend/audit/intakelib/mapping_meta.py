from .constants import (
    SECTION_NAME,
)

from .mapping_util import (
    _set_by_path,
    FieldMapping,
)

meta_mapping: FieldMapping = {
    SECTION_NAME: (f"Meta.{SECTION_NAME}", _set_by_path),
}
