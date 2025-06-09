from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from dissemination.searchlib.search_constants import text_input_delimiters, report_id_delimiters
from config.settings import STATE_ABBREVS


def clean_text_field(text_input, delimiters=text_input_delimiters):
    """
    Clean up a given field. Replace common separators with a newline. Split on the newlines.
    Strip all the resulting elements.
    """
    for delimiter in delimiters:
        text_input = text_input.replace(delimiter, "\n")
    text_input = [x.strip() for x in text_input.splitlines()]
    return text_input


class AdvancedSearchForm(forms.Form):
    # Multiple choice field mappings
    findings_field_mapping = {
        "field_name": [
            "all_findings",
            "is_modified_opinion",
            "is_other_findings",
            "is_material_weakness",
            "is_significant_deficiency",
            "is_other_matters",
            "is_questioned_costs",
            "is_repeat_finding",
        ],
        "friendly_name": [
            "Any findings",
            "Modified opinion",
            "Other findings",
            "Material weakness",
            "Significant deficiency",
            "Other matters",
            "Questioned costs",
            "Repeat finding",
        ],
    }
    entity_type_field_mapping = {
        "field_name": [
            "state",
            "local",
            "tribal",
            "higher-ed",
            "non-profit",
            "unknown",
        ],
        "friendly_name": [
            "State",
            "Local Government",
            "Indian tribe or tribal organization",
            "Institution of Higher Education (IHE)",
            "Non-profit",
            "Unknown",
        ],
    }

    # Multiple choice field Tuples. "choices" variable in field declaration.
    AY_choices = (("all_years", "All years"),) + tuple(
        (x, str(x)) for x in reversed(range(2016, date.today().year + 1))
    )  # (("all_years", "All years"), (2016, "2016"), ..., (currentYear, "currentYear"))
    findings_choices = list(zip(*findings_field_mapping.values()))
    direct_funding_choices = (
        ("direct_funding", "Direct funding"),
        ("passthrough_funding", "Passthrough funding"),
    )
    entity_type_choices = list(zip(*entity_type_field_mapping.values()))
    major_program_choices = (
        ("True", "Y"),
        ("False", "N"),
    )

    # Query params
    agency_name = forms.CharField(required=False)
    aln = forms.CharField(required=False)
    audit_year = forms.MultipleChoiceField(
        choices=AY_choices, initial=[2023], required=False
    )
    auditee_state = forms.CharField(required=False)
    cog_or_oversight = forms.CharField(required=False)
    direct_funding = forms.MultipleChoiceField(
        choices=direct_funding_choices, required=False
    )
    end_date = forms.DateField(required=False)
    entity_name = forms.CharField(required=False)
    entity_type = forms.MultipleChoiceField(choices=entity_type_choices, required=False)
    federal_program_name = forms.CharField(required=False)
    findings = forms.MultipleChoiceField(choices=findings_choices, required=False)
    fy_end_month = forms.CharField(required=False)
    major_program = forms.MultipleChoiceField(
        choices=major_program_choices, required=False
    )
    passthrough_name = forms.CharField(required=False)
    report_id = forms.CharField(required=False)
    start_date = forms.DateField(required=False)
    type_requirement = forms.CharField(required=False)
    uei_or_ein = forms.CharField(required=False)

    # Display params
    limit = forms.CharField(required=False)
    page = forms.CharField(required=False)
    order_by = forms.CharField(required=False)
    order_direction = forms.CharField(required=False)

    def clean_aln(self):
        """
        Clean up the ALN field. Replace common separators with a newline.
        Split on the newlines. Strip all the resulting elements.
        """
        text_input = self.cleaned_data["aln"]
        return clean_text_field(text_input)

    def clean_entity_name(self):
        """
        Clean the name field. We can't trust that separators aren't a part of a name somewhere,
        so just split on newlines.
        """
        text_input = self.cleaned_data["entity_name"]
        return text_input.splitlines()

    def clean_uei_or_ein(self):
        """
        Clean up the UEI/EIN field. Replace common separators with a newline.
        Split on the newlines. Strip all the resulting elements.
        """
        text_input = self.cleaned_data["uei_or_ein"]
        return clean_text_field(text_input)

    def clean_audit_year(self):
        """
        If "All years" is selected, don't include any years.
        """
        audit_year = self.cleaned_data["audit_year"]
        if "all_years" in audit_year:
            return []
        return audit_year

    def clean_major_program(self):
        """
        If 'Any' is selected, don't include the more specific fields.
        """
        major_program = self.cleaned_data["major_program"]
        if "any" in major_program:
            return ["any"]
        return major_program

    def clean_auditee_state(self):
        """
        If the auditee_state is present and is not a valid state (one of STATE_ABBREVS), provide an error.
        """
        auditee_state = self.cleaned_data["auditee_state"]
        if not auditee_state:
            return auditee_state

        if auditee_state not in STATE_ABBREVS:
            raise ValidationError(
                f'"{auditee_state}" is not a valid state abbreviation.'
            )
        return auditee_state

    def clean_fy_end_month(self):
        """
        If the fy_end_month is present and is not a valid month (1-12), provide an error.
        """
        fy_end_month = self.cleaned_data["fy_end_month"]
        if not fy_end_month:
            return fy_end_month

        valid_months = [str(x) for x in range(1, 13)]  # ["1", "2", ..., "12"]
        if fy_end_month not in valid_months:
            raise ValidationError(f'"{fy_end_month}" is not a valid month.')

        return fy_end_month

    def clean_type_requirement(self):
        """
        Clean up the type requirement field. Uppercase all input. Replace common
        separators with a newline. Split on the newlines.
        Strip all the resulting elements.
        """
        text_input = self.cleaned_data["type_requirement"]
        text_input = text_input.upper()
        return clean_text_field(text_input)

    def clean_report_id(self):
        """
        Clean up the report_id field. Uppercase all input. Replace common
        separators (except '-') with a newline. Split on the newlines.
        Strip all the resulting elements.
        """
        text_input = self.cleaned_data["report_id"]
        return clean_text_field(text_input, report_id_delimiters)

    def clean_passthrough_name(self):
        """
        Clean the passthrough name field. We can't trust that separators aren't a part of
        a name somewhere, so just split on newlines.
        """
        text_input = self.cleaned_data["passthrough_name"]
        return text_input.splitlines()

    def clean_federal_program_name(self):
        """
        Clean the federal program name field. We can't trust that separators aren't a part of
        a name somewhere, so just split on newlines.
        """
        text_input = self.cleaned_data["federal_program_name"]
        return text_input.splitlines()

    def clean_page(self):
        """
        Default page number to one.
        """
        try:
            return int(self.cleaned_data["page"] or 1)
        except ValueError:
            raise ValidationError("Page value is not an integer.")

    def clean_limit(self):
        """
        Default page limit to 30.
        """
        try:
            return int(self.cleaned_data["limit"] or 30)
        except ValueError:
            raise ValidationError("Limit value is not an integer.")


class SearchForm(forms.Form):
    # Multiple choice field mappings
    entity_type_field_mapping = {
        "field_name": [
            "state",
            "local",
            "tribal",
            "higher-ed",
            "non-profit",
            "unknown",
        ],
        "friendly_name": [
            "State",
            "Local Government",
            "Indian tribe or tribal organization",
            "Institution of Higher Education (IHE)",
            "Non-profit",
            "Unknown",
        ],
    }

    # Multiple choice field Tuples. "choices" variable in field declaration.
    AY_choices = (("all_years", "All years"),) + tuple(
        (x, str(x)) for x in reversed(range(2016, date.today().year + 1))
    )  # (("all_years", "All years"), (2016, "2016"), ..., (currentYear, "currentYear"))
    entity_type_choices = list(zip(*entity_type_field_mapping.values()))

    # Query params
    audit_year = forms.MultipleChoiceField(
        choices=AY_choices, initial=[2023], required=False
    )
    auditee_state = forms.CharField(required=False)
    end_date = forms.DateField(required=False)
    entity_name = forms.CharField(required=False)
    entity_type = forms.MultipleChoiceField(choices=entity_type_choices, required=False)
    fy_end_month = forms.CharField(required=False)
    report_id = forms.CharField(required=False)
    start_date = forms.DateField(required=False)
    uei_or_ein = forms.CharField(required=False)

    # Display params
    limit = forms.CharField(required=False)
    page = forms.CharField(required=False)
    order_by = forms.CharField(required=False)
    order_direction = forms.CharField(required=False)

    def clean_entity_name(self):
        """
        Clean the name field. We can't trust that separators aren't a part of a name somewhere,
        so just split on newlines.
        """
        text_input = self.cleaned_data["entity_name"]
        return text_input.splitlines()

    def clean_uei_or_ein(self):
        """
        Clean up the UEI/EIN field. Replace common separators with a newline.
        Split on the newlines. Strip all the resulting elements.
        """
        text_input = self.cleaned_data["uei_or_ein"]
        return clean_text_field(text_input)

    def clean_audit_year(self):
        """
        If "All years" is selected, don't include any years.
        """
        audit_year = self.cleaned_data["audit_year"]
        if "all_years" in audit_year:
            return []
        return audit_year

    def clean_auditee_state(self):
        """
        If the auditee_state is present and is not a valid state (one of STATE_ABBREVS), provide an error.
        """
        auditee_state = self.cleaned_data["auditee_state"]
        if not auditee_state:
            return auditee_state

        if auditee_state not in STATE_ABBREVS:
            raise ValidationError(
                f'"{auditee_state}" is not a valid state abbreviation.'
            )
        return auditee_state

    def clean_fy_end_month(self):
        """
        If the fy_end_month is present and is not a valid month (1-12), provide an error.
        """
        fy_end_month = self.cleaned_data["fy_end_month"]
        if not fy_end_month:
            return fy_end_month

        valid_months = [str(x) for x in range(1, 13)]  # ["1", "2", ..., "12"]
        if fy_end_month not in valid_months:
            raise ValidationError(f'"{fy_end_month}" is not a valid month.')

        return fy_end_month

    def clean_report_id(self):
        """
        Clean up the report_id field. Uppercase all input. Replace common
        separators (except '-') with a newline. Split on the newlines.
        Strip all the resulting elements.
        """
        text_input = self.cleaned_data["report_id"]
        return clean_text_field(text_input, report_id_delimiters)

    def clean_page(self):
        """
        Default page number to one.
        """
        try:
            return int(self.cleaned_data["page"] or 1)
        except ValueError:
            raise ValidationError("Page value is not an integer.")

    def clean_limit(self):
        """
        Default page limit to 30.
        """
        try:
            return int(self.cleaned_data["limit"] or 30)
        except ValueError:
            raise ValidationError("Limit value is not an integer.")
