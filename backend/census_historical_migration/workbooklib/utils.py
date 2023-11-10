from census_historical_migration.workbooklib.templates import sections_to_template_paths


def get_template_name_for_section(section):
    """
    Return a workbook template name corresponding to the given section
    """
    if section in sections_to_template_paths:
        template_name = sections_to_template_paths[section].name
        return template_name
    else:
        raise ValueError(f"Unknown section {section}")
