import logging
import math

from django.conf import settings
from audit.models.models import ExcelFile, SingleAuditChecklist, STATUS
from boto3 import client as boto3_client
from botocore.client import ClientError, Config
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger, EmptyPage


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
            if deleted.get("Key", None):
                logger.info(
                    f"Successfully deleted {deleted['Key']} from S3 for report: {sac.report_id}"
                )

        errors = response.get("Errors", [])
        if errors:
            for error in errors:
                if error.get("Key", None):
                    logger.error(
                        f"Failed to delete {error['Key']} from S3 for report: {sac.report_id}. Error: {error['Message']}"  # nosec B608
                    )

    except ClientError as e:
        logger.error(
            f"Failed to delete files from S3 for report: {sac.report_id}. Error: {e}"
        )


def clean_artifacts(sac_list):
    """
    Perform necessary cleanup associated with the given list of sac values.
    """
    try:
        excel_files = ExcelFile.objects.filter(sac__in=sac_list)
        files = [f"excel/{excel_file.filename}" for excel_file in excel_files]

        if files:
            logger.info(
                f"Found {len(files)} ExcelFile records for reports: {[sac.report_id for sac in sac_list]}"
            )

            # Track results but do not delete the ExcelFile records from the database
            successful_deletes, failed_deletes = batch_removal(
                files,
                sac_list,
                {
                    f"excel/{excel_file.filename}": excel_file.sac.report_id
                    for excel_file in excel_files
                },
            )

            if failed_deletes:
                logger.error(
                    f"Failed to delete the following files from S3: {failed_deletes}"
                )
            if successful_deletes:
                logger.info(
                    f"Successfully deleted the following files from S3: {successful_deletes}"
                )

    except Exception as e:
        logger.error(f"Failed to process files for the provided sac values. Error: {e}")


def batch_removal(filenames, sac_list, sac_to_report_id_map):
    """Delete files from S3 in bulk and return the results."""
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

        successful_deletes = []
        failed_deletes = []
        deleted_files = response.get("Deleted", [])
        for deleted in deleted_files:
            filename = deleted["Key"]
            successful_deletes.append(
                {
                    "filename": filename,
                    "sac_report_id": sac_to_report_id_map[filename],
                }
            )

        errors = response.get("Errors", [])
        if errors:
            for error in errors:
                filename = error["Key"]
                failed_deletes.append(
                    {
                        "filename": filename,
                        "sac_report_id": sac_to_report_id_map[filename],
                        "error_message": error["Message"],
                    }
                )

        return successful_deletes, failed_deletes

    except ClientError as e:
        logger.error(
            f"Failed to delete files from S3 for sac values: {[sac.report_id for sac in sac_list]}. Error: {e}"
        )
        return [], [{"error_message": str(e)}]
    except Exception as e:
        logger.error(f"Failed to delete files from S3. Error: {e}")
        return [], [{"error_message": str(e)}]


def delete_workbooks(partition_number, total_partitions, page_size=10, pages=None):
    """Iterates over disseminated reports for the specified partition."""

    if partition_number < 1 or partition_number > total_partitions:
        raise ValueError(
            "Invalid partition number. It must be between 1 and the total number of partitions."
        )

    all_ids = (
        SingleAuditChecklist.objects.filter(submission_status=STATUS.DISSEMINATED)
        .values_list("id", flat=True)
        .order_by("id")
    )

    total_ids = len(all_ids)
    ids_per_partition = math.ceil(total_ids / total_partitions)

    start_index = (partition_number - 1) * ids_per_partition
    end_index = min(partition_number * ids_per_partition, total_ids)

    ids_to_process = all_ids[start_index:end_index]

    sacs = SingleAuditChecklist.objects.filter(id__in=ids_to_process).order_by("id")

    paginator = Paginator(sacs, page_size)
    total_pages = (
        paginator.num_pages if pages is None else min(pages, paginator.num_pages)
    )

    logger.info(
        f"Retrieving {sacs.count()} reports for partition {partition_number} of {total_partitions}"
    )

    for page_number in range(1, total_pages + 1):
        try:
            page = paginator.page(page_number)
            logger.info(
                f"Processing page {page_number} with {page.object_list.count()} reports."
            )

            # Extract sac values from the current page
            sac_list = list(page.object_list)
            clean_artifacts(sac_list)

        except PageNotAnInteger:
            logger.error(f"Page number {page_number} is not an integer.")
        except EmptyPage:
            logger.info(f"No more pages to process after page {page_number}.")
            break
        except Exception as e:
            logger.error(f"An error occurred while processing page {page_number}: {e}")
