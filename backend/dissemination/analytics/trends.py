# Analytics for disseminated records on a yearly basis.

from dissemination.models import (
    FederalAward,
    Finding,
    General,
)
from django.db.models import Sum


class DisseminationTrendAnalytics:

    def __init__(self, years):

        # list of years.
        self.years = years

        # preload queries for faster performance.
        self.records = self._get_records_by_years()
        self.awards = self._get_awards_by_years()
        self.findings = self._get_findings_by_years()

    def _get_records_by_years(self):
        """Get all disseminated records for a specified range of years."""
        return General.objects.filter(
            is_public=True, fac_accepted_date__year__in=self.years
        )

    def _get_awards_by_years(self):
        """Get federal awards based on all the records that were disseminated for a specific range of years."""
        record_ids = self.records.values("report_id")
        return FederalAward.objects.filter(report_id__in=record_ids)

    def _get_findings_by_years(self):
        """Get findings based on all the records that were disseminated for a specific range of years."""
        record_ids = self.records.values("report_id")
        return Finding.objects.filter(report_id__in=record_ids)

    def _get_records_by_year(self, year):
        """Get a record set from a specific year within self.records"""
        return self.records.filter(fac_accepted_date__year=year)

    def total_submissions(self):
        out = []
        for year in self.years:
            out.append(
                {
                    "year": year,
                    "total": self._get_records_by_year(year).count(),
                }
            )
        return out

    def total_award_volume(self):
        out = []
        for year in self.years:
            out.append(
                {
                    "year": year,
                    "total": self.awards.filter(
                        report_id__fac_accepted_date__year=year
                    ).aggregate(Sum("amount_expended"))["amount_expended__sum"]
                    or 0,
                }
            )
        return out

    def total_findings(self):
        out = []
        for year in self.years:
            out.append(
                {
                    "year": year,
                    "total": self.findings.filter(
                        report_id__fac_accepted_date__year=year
                    ).count(),
                }
            )
        return out

    def submissions_with_findings(self):
        out = []
        for year in self.years:
            audits_count = self._get_records_by_year(year).count()
            findings_count = (
                self._get_records_by_year(year).exclude(finding=None).count()
            )
            out.append(
                {
                    "year": year,
                    "total": (
                        (findings_count / audits_count) * 100 if audits_count > 0 else 0
                    ),
                }
            )
        return out

    def auditee_risk_profile(self):
        out = []
        for year in self.years:
            total = self._get_records_by_year(year).count()
            low_risk_count = (
                self._get_records_by_year(year)
                .filter(is_low_risk_auditee="Yes")
                .count()
            )
            not_low_risk_count = total - low_risk_count

            out.append(
                {
                    "year": year,
                    "low_risk": low_risk_count,
                    "low_risk_percent": (
                        (low_risk_count / total) * 100 if total > 0 else 0
                    ),
                    "not_low_risk": not_low_risk_count,
                    "not_low_risk_percent": (
                        (not_low_risk_count / total) * 100 if total > 0 else 0
                    ),
                }
            )
        return out

    def risk_profile_vs_findings(self):
        out = []
        for year in self.years:
            not_low_risk_count = (
                self._get_records_by_year(year).filter(is_low_risk_auditee="No").count()
            )
            findings_count = (
                self._get_records_by_year(year).exclude(finding=None).count()
            )
            total = self._get_records_by_year(year).count()
            out.append(
                {
                    "year": year,
                    "not_low_risk": (
                        (not_low_risk_count / total) * 100 if total > 0 else 0
                    ),
                    "audits_with_findings": (
                        (findings_count / total) * 100 if total > 0 else 0
                    ),
                }
            )
        return out
