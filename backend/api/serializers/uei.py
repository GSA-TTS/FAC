import json

from rest_framework import serializers

from api.uei import get_uei_info_from_sam_gov


class UEISerializer(serializers.Serializer):
    """
    Does a UEI request against the SAM.gov API and returns a flattened shape
    containing only the fields we're interested in.

    The below operations are nested and mixed among functions, rather than done
    serially, but the approximate order of operations is:

        +   Assemble the parameters to pass to the API.
            Mostly in api.uei.get_uei_info_from_sam_gov.
        +   Make the API request.
            api.uei.call_sam_api
        +   Check for high-level errors.
            api.uei.get_uei_info_from_sam_gov
        +   Extract the JSON for the individual record out of the response and check
        for some other errors.
            api.uei.parse_sam_uei_json
        +   For a specific class of error, retry the API call with different
        parameters.
            api.uei.get_uei_info_from_sam_gov
            api.uei.call_sam_api
            api.uei.parse_sam_uei_json
        +   If we don't have errors by that point, flatten the data.
            api.serializers.UEISerializer.validate_auditee_uei
        +   If we don't encounter errors at that point, return the flattened data.
            api.serializers.UEISerializer.validate_auditee_uei

    """

    auditee_uei = serializers.CharField()

    def validate_auditee_uei(self, value):
        """
        Flattens the UEI response info and returns this shape:

            {
                "auditee_uei": …,
                "auditee_name": …,
                "auditee_fiscal_year_end_date": …,
                "auditee_address_line_1": …,
                "auditee_city": …,
                "auditee_state": …,
                "auditee_zip": …,
            }

        Will provide default error-message-like values (such as “No address in SAM.gov)
        if the keys are missing, but if the SAM.gov fields are present but empty, we
        return the empty strings.

        """
        sam_response = get_uei_info_from_sam_gov(value)
        if sam_response.get("errors"):
            raise serializers.ValidationError(sam_response.get("errors"))

        entity_registration = sam_response.get("response")["entityRegistration"]
        core = sam_response.get("response")["coreData"]

        basic_data = {
            "auditee_uei": value,
            "auditee_name": entity_registration.get("legalBusinessName"),
        }
        addr_key = "mailingAddress" if "mailingAddress" in core else "physicalAddress"

        mailing_data = {
            "auditee_address_line_1": "No address in SAM.gov.",
            "auditee_city": "No address in SAM.gov.",
            "auditee_state": "No address in SAM.gov.",
            "auditee_zip": "No address in SAM.gov.",
        }

        if addr_key in core:
            mailing_data = {
                "auditee_address_line_1": core.get(addr_key).get("addressLine1"),
                "auditee_city": core.get(addr_key).get("city"),
                "auditee_state": core.get(addr_key).get("stateOrProvinceCode"),
                "auditee_zip": core.get(addr_key).get("zipCode"),
            }

        # 2023-10-10: Entities with a samRegistered value of No may be missing
        # some fields from coreData entirely.
        entity_information = core.get("entityInformation", {})
        extra_data = {
            "auditee_fiscal_year_end_date": entity_information.get(
                "fiscalYearEndCloseDate", "No fiscal year end date in SAM.gov."
            ),
        }
        return json.dumps(basic_data | mailing_data | extra_data)
