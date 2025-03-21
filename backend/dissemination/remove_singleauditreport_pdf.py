import logging

from audit.models.files import SingleAuditReportFile

from dissemination.remove_workbook_artifacts import delete_files_in_bulk


logger = logging.getLogger(__name__)


def remove_singleauditreport_pdf(sac):
    """
    Remove the single audit report pdf associated with the given sac.
    """
    try:
        files = SingleAuditReportFile.objects.filter(sac=sac)
        files = [f"singleauditreport/{file.filename}" for file in files]
        if files:
            # Delete the files from S3 in bulk
            delete_files_in_bulk(files, sac)

    except SingleAuditReportFile.DoesNotExist:
        logger.info(
            f"No single audit report file found to delete for report: {sac.report_id}"
        )
    except Exception as e:
        logger.error(
            f"Failed to delete files from S3 for report: {sac.report_id}. Error: {e}"
        )
