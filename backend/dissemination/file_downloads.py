import logging

from django.conf import settings
from django.http import Http404

from boto3 import client as boto3_client
from botocore.client import ClientError, Config

from audit.models import ExcelFile, SingleAuditReportFile, Audit
from audit.models.constants import STATUS

logger = logging.getLogger(__name__)


def get_filename(report_id, file_type):
    audit = Audit.objects.filter(
        report_id=report_id, submission_status=STATUS.DISSEMINATED
    ).first()
    if file_type == "report":
        try:
            if audit:
                file_obj = SingleAuditReportFile.objects.filter(audit=audit).latest(
                    "date_created"
                )
                return f"singleauditreport/{file_obj.filename}"
            else:
                if settings.CENSUS_DATA_SOURCE in report_id:
                    return f"singleauditreport/{report_id}.pdf"
                else:
                    raise Http404()
        except SingleAuditReportFile.DoesNotExist:
            raise Http404()
    else:
        try:
            file_obj = ExcelFile.objects.filter(
                audit=audit, form_section=file_type
            ).latest("date_created")
            return f"excel/{file_obj.filename}"
        except ExcelFile.DoesNotExist:
            raise Http404()


def file_exists(filename, show_warning=True):
    # this client uses the internal endpoint url because we're making a request to S3 from within the app
    s3_client = boto3_client(
        service_name="s3",
        region_name=settings.AWS_S3_PRIVATE_REGION_NAME,
        aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_PRIVATE_INTERNAL_ENDPOINT,
        config=Config(signature_version="s3v4"),
    )

    try:
        s3_client.head_object(
            Bucket=settings.AWS_PRIVATE_STORAGE_BUCKET_NAME,
            Key=filename,
        )

        return True
    except ClientError:
        if show_warning:
            logger.warn(f"Unable to locate file {filename} in S3!")
        return False


def get_download_url(filename):
    try:
        # this client uses the external endpoint url because we're generating a request URL that is eventually triggered from outside the app
        s3_client = boto3_client(
            service_name="s3",
            region_name=settings.AWS_S3_PRIVATE_REGION_NAME,
            aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_PRIVATE_EXTERNAL_ENDPOINT,
            config=Config(signature_version="s3v4"),
        )

        if file_exists(filename):
            # Remove directory information
            nicer_filename = filename.split("/")[-1]
            response = s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": settings.AWS_PRIVATE_STORAGE_BUCKET_NAME,
                    "Key": filename,
                    "ResponseContentDisposition": f"attachment;filename={nicer_filename}",
                },
                ExpiresIn=30,
            )

            return response
        else:
            raise Http404("File not found")
    except ClientError:
        raise Http404("File not found")
