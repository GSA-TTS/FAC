from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from boto3 import client as boto3_client
from botocore.client import ClientError, Config

from audit.models import ExcelFile, SingleAuditChecklist, SingleAuditReportFile


def get_filename(sac, file_type):
    if file_type == "report":
        file_obj = get_object_or_404(SingleAuditReportFile, sac=sac)
        return f"singleauditreport/{file_obj.filename}"
    else:
        file_obj = get_object_or_404(ExcelFile, sac=sac, form_section=file_type)
        return f"excel/{file_obj.filename}"


def get_download_url(filename):
    try:
        s3_client = boto3_client(
            service_name="s3",
            region_name=settings.AWS_S3_PRIVATE_REGION_NAME,
            aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_PRIVATE_EXTERNAL_ENDPOINT,
            config=Config(signature_version="s3v4"),
        )

        response = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": settings.AWS_PRIVATE_STORAGE_BUCKET_NAME,
                "Key": filename,
                "ResponseContentDisposition": f"attachment;filename={filename}",
            },
            ExpiresIn=30,
        )

        return response
    except ClientError:
        raise Http404("File not found")


class FileDownloadView(generic.View):
    def get(self, request, report_id, file_type):
        sac = get_object_or_404(SingleAuditChecklist, report_id=report_id)

        if not sac.is_public:
            # if user has access via Access object
            #     proceed
            # elif none, check if user is among the blessed
            #     proceed
            # else
            raise PermissionDenied("You do not have access to this audit report.")

        filename = get_filename(sac, file_type)
        return redirect(get_download_url(filename))


class ApiFileDownloadView(generic.View):
    def get(self, request, report_id, file_type, token):
        sac = get_object_or_404(SingleAuditChecklist, report_id=report_id)

        if not sac.is_public:
            # if token found in... file.. download.. tokens.. table
            #    token.delete()
            #    proceed
            # else
            raise PermissionDenied("You do not have access to this audit report.")

        filename = get_filename(sac, file_type)
        return get_download_url(filename)
