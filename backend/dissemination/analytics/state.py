# Analytics for disseminated records at the state level.

from dissemination.models import (
    FederalAward,
    General,
)
from django.db.models import (
    Count,
    F,
    Sum,
    Q
)

class DisseminationStateAnalytics:

    def __init__(self, year, state):
        self.year = year
        self.state = state

        # preload queries for faster performance.
        self.records = self._get_records_by_state_and_year()
        self.awards = self._get_awards_by_year()

    def _get_records_by_state_and_year(self):
        """ Get all disseminated records for a specified year and state. """
        return General.objects.filter(
            is_public=True,
            auditee_state=self.state,
            fac_accepted_date__year=self.year
        )

    def _get_awards_by_year(self):
        """ Get federal awards based on all the records that were disseminated for a specific state and year. """
        record_ids = self.records.values('report_id')
        return FederalAward.objects.filter(report_id__in=record_ids)

    def single_dissemination_count(self):
        out = {
            "total": self.records.count()
        }
        return out

    def top_programs(self):
        """ Top funded federal programs. """
        out = list(
            self.awards
            .values('federal_program_name')
            .annotate(total_expended=Sum('amount_expended'))
            .order_by('-total_expended')
        )
        return out

    def funding_by_entity_type(self):
        """ Top funded federal programs based on entity type. """
        out = list(
            self.awards
            .values(entity_type=F('report_id__entity_type'))
            .annotate(total_expended=Sum('amount_expended'))
            .order_by('-total_expended')
        )
        return out

    def funding_by_county(self):
        """ Top funded federal programs based on county. """
        # TODO: Analytics Dashboard
        # How do we get counties?
        pass

    def programs_with_repeated_findings(self):
        """ Top federal programs with repeated findings. """
        awards = self.awards.filter(report_id__finding__is_repeat_finding='Y')
        out = list(
            awards
            .values('federal_program_name')
            .annotate(
                repeat_findings=Count(
                    'report_id__finding',
                    filter=Q(report_id__finding__is_repeat_finding='Y'),
                    distinct=True
                )
            )
            .order_by('-repeat_findings')
        )
        return out

    def top_state_entities_with_questioned_costs(self):
        # TODO: Analytics Dashboad
        # We don't store questioned costs yet.
        pass
