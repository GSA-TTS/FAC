from dissemination.file_downloads import file_exists
from django.conf import settings
from django.shortcuts import redirect
import boto3

LOCAL_FILENAME = "./runtime/MAINTENANCE_MODE"
S3_FILENAME = "runtime/MAINTENANCE_MODE"


def is_maintenance_on():
    """
    Get current status of maintenance mode.
    """

    return file_exists(S3_FILENAME)


def change_maintenance(enabled):
    """
    Update status of maintenance mode.
    """

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    )

    # turn on.
    if enabled:
        s3_client.put_object(
            Bucket=settings.AWS_PRIVATE_STORAGE_BUCKET_NAME,
            Body=LOCAL_FILENAME,
            Key=S3_FILENAME,
        )

    # turn off.
    else:
        if file_exists(S3_FILENAME):
            s3_client.delete_object(
                Bucket=settings.AWS_PRIVATE_STORAGE_BUCKET_NAME, Key=S3_FILENAME
            )


class MaintenanceCheck:
    """
    Middleware that prevents clients from accessing the
    FAC application so long as "MAINTENANCE_MODE" (a file in
    the S3 bucket) exists.
    """

    def __init__(self, get_response):
        """Initializes the middleware."""

        self.get_response = get_response

    def __call__(self, request):
        """
        Check that maintenance mode is disabled before running request.
        """

        # redirect to maintenance page.
        if is_maintenance_on():
            if request.path != "/maintenance":
                return redirect("/maintenance")

        else:
            # redirect to home page if on maintenance.
            if request.path == "/maintenance":
                return redirect("/")

        response = self.get_response(request)
        return response
