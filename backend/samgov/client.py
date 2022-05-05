from django.conf import settings
import requests


class SAMClient(object):
    """
    SAM.gov Entity Management API Client
    """

    def __init__(self, api_root=None, api_auth_token=None):
        self.api_root = api_root or settings.SAM_ENTITY_API_URL
        self.api_auth_token = api_auth_token or settings.SAM_API_KEY
        self.headers = {"X-Api-key": self.api_auth_token}

    def get_entity(self, uei=None):
        """
        GET w/ parameters to
        """
        response = requests.get(
            url=self.api_root,
            params={
                "ueiSAM": uei,
                "samRegistered": "Yes",
                "includeSections": "entityRegistration",
            },
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    def get_entity_legal_name(self, uei=None):
        """For a given UEI, return an entities LegalName"""
        entity_data_from_sam = self.get_entity(uei=uei)

        if entity_data_from_sam["totalRecords"] == 1:
            return entity_data_from_sam["entityData"][0]["entityRegistration"][
                "legalBusinessName"
            ]

        if entity_data_from_sam["totalRecords"] == 0:
            raise ValueError(f"No active registration reported by SAM.gov for {uei}")

        raise ValueError(f"Multiple active registrations reported by SAM.gov for {uei}")
