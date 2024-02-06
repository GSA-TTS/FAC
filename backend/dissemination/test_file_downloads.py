from datetime import datetime

from django.conf import settings
from django.http import Http404
from django.test import TestCase

from audit.fixtures.excel import FORM_SECTIONS
from audit.models import (
    ExcelFile,
    generate_sac_report_id,
    SingleAuditChecklist,
    SingleAuditReportFile,
)
from dissemination.file_downloads import get_filename

from model_bakery import baker


class GetFilenameTests(TestCase):
    def setUp(self):
        pass

    def _report_id(self, source):
        today = datetime.utcnow().date().isoformat()
        return generate_sac_report_id(today, source)

    def test_gsafac_no_singleauditchecklist(self):
        """
        Given a report ID associated with a GSAFAC sourced SAC, for which there is no SingleAuditChecklist
        When get_filename is called for that report ID
        Then get_filename should throw an Http404 error
        """
        report_id = self._report_id("GSAFAC")

        self.assertRaises(Http404, get_filename, report_id, "report")

        for form_section in FORM_SECTIONS:
            self.assertRaises(Http404, get_filename, report_id, form_section)

    def test_gsafac_no_singleauditreportfile(self):
        """
        Given a report ID associated with a GSAFAC sourced SAC, for which there is no SingleAuditReportFile
        When get_filename is called for that report ID
        Then get_filename should throw an Http404 error
        """
        report_id = self._report_id("GSAFAC")

        baker.make(SingleAuditChecklist, report_id=report_id)

        self.assertRaises(Http404, get_filename, report_id, "report")

    def test_gsafac_with_singleauditreportfile(self):
        """
        Given a report ID associated with a GSAFAC sourced SAC, for which there is a SingleAuditReportFile
        When get_filename is called for that report ID
        Then get_filename should return a valid filename
        """
        report_id = self._report_id("GSAFAC")

        sac = baker.make(SingleAuditChecklist, report_id=report_id)
        baker.make(SingleAuditReportFile, sac=sac)

        filename = get_filename(report_id, "report")

        self.assertEquals(f"singleauditreport/{report_id}.pdf", filename)

    def test_gsafac_no_excelfile(self):
        """
        Given a report ID associated with a GSAFAC sourced SAC, for which there is no ExcelFile
        When get_filename is called for that report ID
        Then get_filename should throw an Http404 error
        """
        report_id = self._report_id("GSAFAC")

        baker.make(SingleAuditChecklist, report_id=report_id)

        for form_section in FORM_SECTIONS:
            self.assertRaises(Http404, get_filename, report_id, form_section)

    def test_gsafac_with_excelfile(self):
        """
        Given a report ID associated with a GSAFAC sourced SAC, for which there is an ExcelFile
        When get_filename is called for that report ID
        Then get_filename should return a valid filename
        """
        report_id = self._report_id("GSAFAC")

        sac = baker.make(SingleAuditChecklist, report_id=report_id)

        for form_section in FORM_SECTIONS:
            baker.make(ExcelFile, sac=sac, form_section=form_section)

            filename = get_filename(report_id, form_section)
            self.assertEquals(f"excel/{report_id}--{form_section}.xlsx", filename)

    def test_census_no_singleauditchecklist(self):
        """
        Given a report ID associated with a CENSUS sourced SAC, for which there is no SingleAuditChecklist
        When get_filename is called for that report ID
        Then get_filename should return a valid filename
        """
        report_id = self._report_id(settings.CENSUS_DATA_SOURCE)

        filename = get_filename(report_id, "report")

        self.assertEquals(f"singleauditreport/{report_id}.pdf", filename)

    def test_census_no_singleauditreportfile(self):
        """
        Given a report ID associated with a CENSUS sourced SAC, for which there is no SingleAuditReportFile
        When get_filename is called for that report ID
        Then get_filename should return a valid
        """
        report_id = self._report_id("GSAFAC")

        baker.make(SingleAuditChecklist, report_id=report_id)

        self.assertRaises(Http404, get_filename, report_id, "report")

    def test_census_with_singleauditreportfile(self):
        """
        Given a report ID associated with a CENSUS sourced SAC, for which there is a SingleAuditReportFile
        When get_filename is called for that report ID
        Then get_filename should return a valid filename
        """
        report_id = self._report_id(settings.CENSUS_DATA_SOURCE)

        sac = baker.make(SingleAuditChecklist, report_id=report_id)
        baker.make(SingleAuditReportFile, sac=sac)

        filename = get_filename(report_id, "report")

        self.assertEquals(f"singleauditreport/{report_id}.pdf", filename)

    def test_census_no_excelfile(self):
        """
        Given a report ID associated with a CENSUS sourced SAC, for which there is no ExcelFile
        When get_filename is called for that report ID
        Then get_filename should throw an Http404 error
        """
        report_id = self._report_id(settings.CENSUS_DATA_SOURCE)

        baker.make(SingleAuditChecklist, report_id=report_id)

        for form_section in FORM_SECTIONS:
            self.assertRaises(Http404, get_filename, report_id, form_section)

    def test_census_with_excelfile(self):
        """
        Given a report ID associated with a CENSUS sourced SAC, for which there is an ExcelFile
        When get_filename is called for that report ID
        Then get_filename should return a valid filename
        """
        report_id = self._report_id(settings.CENSUS_DATA_SOURCE)

        sac = baker.make(SingleAuditChecklist, report_id=report_id)

        for form_section in FORM_SECTIONS:
            baker.make(ExcelFile, sac=sac, form_section=form_section)

            filename = get_filename(report_id, form_section)
            self.assertEquals(f"excel/{report_id}--{form_section}.xlsx", filename)
