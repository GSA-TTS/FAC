import json
from typing import List

from django.http import Http404, HttpResponse, JsonResponse
from django.views import generic
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView

from config.settings import AUDIT_SCHEMA_DIR, BASE_DIR


class Sprite(generic.View):
    """
    Due to problematic interactions between the SVG use element and
    cross-domain rules and serving assets from S3, we need to serve this
    particular file from Django.
    """

    def get(self, _request):
        """Grab the file from static and return its contents as an image."""
        fpath = BASE_DIR / "static" / "img" / "sprite.svg"
        return HttpResponse(
            content=fpath.read_text(encoding="utf-8"), content_type="image/svg+xml"
        )


class SchemaView(APIView):
    """
    Returns the JSON schema for the specified fiscal year
    """

    # this is a public endpoint - no authentication or permission required
    authentication_classes: List[BaseAuthentication] = []
    permission_classes: List[BasePermission] = []

    def get(self, _, fiscal_year, schema_type):
        """GET JSON schema for the specified fiscal year"""
        fpath = AUDIT_SCHEMA_DIR / f"{fiscal_year}-{schema_type}.json"

        if not fpath.exists():
            raise Http404()

        return JsonResponse(json.loads(fpath.read_text(encoding="utf-8")))
