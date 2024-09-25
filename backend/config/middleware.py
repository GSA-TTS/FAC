from config.settings import MAINTENANCE
from django.shortcuts import redirect

class MaintenanceCheck:
    def __init__(self, get_response):
        """Initializes the middleware."""

        self.get_response = get_response

    def __call__(self, request):
        """
        Check that maintenance mode is disabled before running request.
        """

        if MAINTENANCE:
            return redirect(f"/SOME_MAINTENANCE_HTML")

        response = self.get_response(request)
        return response
