import logging

from django.conf import settings
from audit.models.models import ExcelFile
from boto3 import client as boto3_client
from botocore.client import ClientError, Config

logger = logging.getLogger(__name__)


def remove_workbook_artifacts(sac):
    """
    Remove all workbook artifacts associated with the given sac.
    """
    try:
        excel_files = ExcelFile.objects.filter(sac=sac)
        files = [f"excel/{excel_file.filename}" for excel_file in excel_files]

        if files:
            # Delete the files from S3 in bulk
            delete_files_in_bulk(files, sac)

    except ExcelFile.DoesNotExist:
        logger.info(f"No files found to delete for report: {sac.report_id}")
    except Exception as e:
        logger.error(
            f"Failed to delete files from S3 for report: {sac.report_id}. Error: {e}"
        )


def delete_files_in_bulk(filenames, sac):
    """Delete files from S3 in bulk."""
    # This client uses the internal endpoint URL because we're making a request to S3 from within the app
    s3_client = boto3_client(
        service_name="s3",
        region_name=settings.AWS_S3_PRIVATE_REGION_NAME,
        aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_PRIVATE_INTERNAL_ENDPOINT,
        config=Config(signature_version="s3v4"),
    )

    try:
        delete_objects = [{"Key": filename} for filename in filenames]

        response = s3_client.delete_objects(
            Bucket=settings.AWS_PRIVATE_STORAGE_BUCKET_NAME,
            Delete={"Objects": delete_objects},
        )

        deleted_files = response.get("Deleted", [])
        for deleted in deleted_files:
            logger.info(
                f"Successfully deleted {deleted['Key']} from S3 for report: {sac.report_id}"
            )

        errors = response.get("Errors", [])
        if errors:
            for error in errors:
                logger.error(
                    f"Failed to delete {error['Key']} from S3 for report: {sac.report_id}. Error: {error['Message']}"  # nosec B608
                )

    except ClientError as e:
        logger.error(
            f"Failed to delete files from S3 for report: {sac.report_id}. Error: {e}"
        )
