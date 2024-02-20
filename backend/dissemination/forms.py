from django import forms


class SearchForm(forms.Form):
    AY_choices = (
        (x, str(x)) for x in reversed(range(2016, 2024))
    )  # ((2016, "2016"), (2017, "2017"), ..., (2023, "2023"))

    findings_choices = list(
        map(
            lambda a, b: (b, a),
            [
                "Modified opinion",
                "Other findings",
                "Material weakness",
                "Significant deficiency",
                "Other matters",
                "Questioned costs",
                "Repeat finding",
            ],
            [
                "is_modified_opinion",
                "is_other_findings",
                "is_material_weakness",
                "is_significant_deficiency",
                "is_other_matters",
                "is_questioned_costs",
                "is_repeat_finding",
            ],
        )
    )

    direct_funding_choices = (
        ("direct_funding", "Direct funding"),
        ("passthrough_funding", "Passthrough funding"),
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
    auditee_state = forms.CharField(required=False)

    # Display params
    limit = forms.CharField(required=False)
    page = forms.CharField(required=False)
    order_by = forms.CharField(required=False)
    order_direction = forms.CharField(required=False)

    def clean_aln(self):
        text_input = self.cleaned_data["aln"]
        text_input = (
            text_input.replace(",", "\n")
            .replace(":", "\n")
            .replace(";", "\n")
            .replace("-", "\n")
        )
        text_input = [x.strip() for x in text_input.splitlines()]
        return text_input

    def clean_entity_name(self):
        text_input = self.cleaned_data["entity_name"]

        return text_input.splitlines()

    def clean_uei_or_ein(self):
        """
        Clean up the UEI/EIN field. Replace common separators with a newline.
        Split on the newlines. Strip all the resulting elements.
        """
        text_input = self.cleaned_data["uei_or_ein"]
        text_input = (
            text_input.replace(",", "\n")
            .replace(":", "\n")
            .replace(";", "\n")
            .replace("-", "\n")
            .replace(" ", "\n")
        )
        text_input = [x.strip() for x in text_input.splitlines()]
        return text_input
    
    def clean_aln(self):
        """
        Clean up the UEI/EIN field. Replace common separators with a newline.
        Split on the newlines. Strip all the resulting elements.
        """
        text_input = self.cleaned_data["aln"]
        text_input = (
            text_input.replace(",", "\n")
            .replace(":", "\n")
            .replace(";", "\n")
            .replace("-", "\n")
            .replace(" ", "\n")
        )
        text_input = [x.strip() for x in text_input.splitlines()]
        return text_input

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
