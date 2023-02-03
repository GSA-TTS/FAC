from django.conf import settings
from django.contrib.auth import authenticate, login


def authenticate_test_user(get_response):
    """
    Middleware that invokes the authentication and login flow automatically incoming requests
    using a test username. This middleware should ONLY be enabled in testing/CI scenarios
    that need to bypass the OIDC login flow
    """

    def middleware(request):
        user = authenticate(request, username=settings.TEST_USERNAME)

        login(request, user)

        response = get_response(request)

        return response

    return middleware
