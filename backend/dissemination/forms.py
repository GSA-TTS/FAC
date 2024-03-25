from django import forms


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

    # Multiple choice field Tuples. "choices" variable in field declaration.
    AY_choices = (("all_years", "All years"),) + tuple(
        (x, str(x)) for x in reversed(range(2016, 2024))
    )
    findings_choices = list(zip(*findings_field_mapping.values()))
    direct_funding_choices = (
        ("direct_funding", "Direct funding"),
        ("passthrough_funding", "Passthrough funding"),
    )
    major_program_choices = (
        (True, "Y"),
        (False, "N"),
    )

    # Query params
    entity_name = forms.CharField(required=False)
    uei_or_ein = forms.CharField(required=False)
    aln = forms.CharField(required=False)
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    cog_or_oversight = forms.CharField(required=False)
    agency_name = forms.CharField(required=False)
    audit_year = forms.MultipleChoiceField(
        choices=AY_choices, initial=[2023], required=False
    )
    findings = forms.MultipleChoiceField(choices=findings_choices, required=False)
    direct_funding = forms.MultipleChoiceField(
        choices=direct_funding_choices, required=False
    )
    major_program = forms.MultipleChoiceField(
        choices=major_program_choices, required=False
    )
    auditee_state = forms.CharField(required=False)

    # Display params
    limit = forms.CharField(required=False)
    page = forms.CharField(required=False)
    order_by = forms.CharField(required=False)
    order_direction = forms.CharField(required=False)

    # Variables for cleaning functions
    text_input_delimiters = [
        ",",
        ":",
        ";",
        "-",
        " ",
    ]

    def clean_aln(self):
        """
        Clean up the ALN field. Replace common separators with a newline.
        Split on the newlines. Strip all the resulting elements.
        """
        text_input = self.cleaned_data["aln"]
        for delimiter in self.text_input_delimiters:
            text_input = text_input.replace(delimiter, "\n")
        text_input = [x.strip() for x in text_input.splitlines()]
        return text_input

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
        for delimiter in self.text_input_delimiters:
            text_input = text_input.replace(delimiter, "\n")
        text_input = [x.strip() for x in text_input.splitlines()]
        return text_input

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

    def clean_page(self):
        """
        Default page number to one.
        """
        return int(self.cleaned_data["page"] or 1)

    def clean_limit(self):
        """
        Default page limit to 30.
        """
        return int(self.cleaned_data["limit"] or 30)


class SearchForm(forms.Form):
    # Multiple choice field Tuples. "choices" variable in field declaration.
    AY_choices = (("all_years", "All years"),) + tuple(
        (x, str(x)) for x in reversed(range(2016, 2024))
    )

    # Query params
    entity_name = forms.CharField(required=False)
    uei_or_ein = forms.CharField(required=False)
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    agency_name = forms.CharField(required=False)
    audit_year = forms.MultipleChoiceField(
        choices=AY_choices, initial=[2023], required=False
    )
    auditee_state = forms.CharField(required=False)

    # Display params
    limit = forms.CharField(required=False)
    page = forms.CharField(required=False)
    order_by = forms.CharField(required=False)
    order_direction = forms.CharField(required=False)

    # Variables for cleaning functions
    text_input_delimiters = [
        ",",
        ":",
        ";",
        "-",
        " ",
    ]

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
        for delimiter in self.text_input_delimiters:
            text_input = text_input.replace(delimiter, "\n")
        text_input = [x.strip() for x in text_input.splitlines()]
        return text_input

    def clean_audit_year(self):
        """
        If "All years" is selected, don't include any years.
        """
        audit_year = self.cleaned_data["audit_year"]
        if "all_years" in audit_year:
            return []
        return audit_year

    def clean_page(self):
        """
        Default page number to one.
        """
        return int(self.cleaned_data["page"] or 1)

    def clean_limit(self):
        """
        Default page limit to 30.
        """
        return int(self.cleaned_data["limit"] or 30)
