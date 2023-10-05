import logging

from django.shortcuts import render
from django.views import generic

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


class AuditSearchView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(self.request, "audit/search.html")
