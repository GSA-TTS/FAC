import csv

from data_distro.management.commands.handle_errors import handle_badlines


# shared settings
panda_shared = {
    "sep": "|",
    "encoding": "mac-roman",
    "on_bad_lines": handle_badlines,
    "engine": "python",
}

# For loading lists like eins_list, and duns_list it can't be loaded in chunks because we need to sort the data frame first to ensure the objects are added in the right order.
panda_config_base = panda_shared | {"quoting": csv.QUOTE_NONE}

# Most tables are processed better without quotes
panda_config = panda_config_base | {"chunksize": 30000, "quoting": csv.QUOTE_NONE}

# Formatted tables need quotes
panda_config_formatted = panda_shared | {"chunksize": 30000}
