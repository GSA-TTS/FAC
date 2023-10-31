# The Unique Entity ID is a 12-character, alphanumeric value that adheres to the following rules:
# The letters “O” and “I” are not used to avoid confusion with zero and one.
# The first character is not zero to avoid cutting off digits that can occur during data imports, for example, when importing data into spreadsheet programs.
# Nine-digit sequences are not used in the identifier to avoid collision with the nine-digit DUNS Number or Taxpayer Identification Number (TIN).
# The first five characters are structured to avoid collision with the Commercial and Government Entity code formatting or CAGE code.
# The Unique Entity ID is not case sensitive.
# The final character is a checksum of the first 11 characters. Checksums are used to detect errors within data.
# The Unique Entity ID does not contain the entity’s Electronic Funds Transfer (EFT) Indicator. The EFT Indicator is a separate field in SAM.gov.
# The “EFT Indicator” in SAM.gov was formally labeled “DUNS+4.”
# The EFT Indicator in SAM.gov is used to identify additional bank accounts associated with a single SAM.gov registration. The EFT Indicator is a separate field from the Unique Entity ID field in SAM.gov.
# The EFT Indicator is determined by the entity during registration.
# The DUNS+4 data provided by entities did not change when the field was re-labeled to “EFT Indicator."
# When a Unique Entity ID was assigned to an entity registration in SAM.gov, the existing EFT Indicator data did not change.
import re
from dissemination.historiclib.exceptions import MigrationMappingError

# EXAMPLE CODE
# This needs to be improved.
# If a mapping fails, we should raise a mapping exception,
# catch that exception, and use it to log when a migration fails.
def to_uei(s):
    if re.search("I|O", s):
        raise MigrationMappingError(source=s)
    else:
        return s
