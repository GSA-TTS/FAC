import logging

from django.views import generic
from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import F, Q
from django.db.transaction import TransactionManagementError
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from audit.mixins import (
    CertifyingAuditeeRequiredMixin,
)
from audit.models import (
    Audit,
    Access,
)
from audit.models.constants import STATUS
from audit.models.utils import generate_audit_indexes, get_friendly_submission_status
from audit.models.viewflow import audit_transition
from audit.decorators import verify_status
from dissemination.remove_workbook_artifacts import audit_remove_workbook_artifacts

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


class MySubmissions(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):
        template_name = "audit/audit_submissions/audit_submissions.html"
        new_link = "report_submission"
        edit_link = "audit:EditSubmission"
        submissions = MySubmissions.fetch_my_submissions(request.user)

        data = {"completed_audits": [], "in_progress_audits": []}
        for audit in submissions:
            audit["submission_status"] = get_friendly_submission_status(
                audit["submission_status"]
            )
            if audit["submission_status"] in ["Submitted", "Disseminated"]:
                data["completed_audits"].append(audit)
            else:
                data["in_progress_audits"].append(audit)

        context = {
            "data": data,
            "new_link": new_link,
            "edit_link": edit_link,
        }
        return render(request, template_name, context)

    @classmethod
    def fetch_my_submissions(cls, user):
        """
        Get all submissions the user is associated with via Access objects.
        """
        accesses = Access.objects.filter(user=user)
        audit_ids = [access.audit.id for access in accesses]
        data = Audit.objects.filter(
            Q(id__in=audit_ids) & ~Q(submission_status=STATUS.FLAGGED_FOR_REMOVAL)
        ).values(
            "report_id",
            "submission_status",
            "auditee_uei",
            "auditee_name",
            fiscal_year_end_date=F(
                "audit__general_information__auditee_fiscal_period_end"
            ),
        )
        return data


class EditSubmission(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        return redirect(reverse("audit", args=[report_id]))


class SubmissionView(CertifyingAuditeeRequiredMixin, generic.View):
    @verify_status(STATUS.AUDITEE_CERTIFIED)
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        try:
            audit = Audit.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": audit.submission_status,
            }

            return render(request, "audit/submission.html", context)
        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.AUDITEE_CERTIFIED)
    def post(self, request, *args, **kwargs):
        # TODO: Post SOT, we should spend time to determine if this is still an issue.
        # RACE HAZARD WARNING
        # It is possible for a user to enter the submission multiple times,
        # from multiple FAC instances. This race hazard is documented in
        # backend/audit/views/README-fac-views-race-hazard-postmortem.md
        report_id = kwargs["report_id"]
        try:
            # remove try/except once we are ready to deprecate SAC.
            audit = Audit.objects.get(report_id=report_id)
            audit_errors = audit.validate()
            if audit_errors:
                context = {"report_id": report_id, "errors": audit_errors}

                return render(
                    request,
                    "audit/cross-validation/cross-validation-results.html",
                    context,
                )

            # Only change this value if things work...
            disseminated = "DID NOT DISSEMINATE"

            # BEGIN ATOMIC BLOCK
            with transaction.atomic():
                audit_transition(request=request, audit=audit, event=STATUS.SUBMITTED)
                audit_indexes = generate_audit_indexes(audit)
                audit.audit.update(audit_indexes)
                audit_transition(
                    request=request, audit=audit, event=STATUS.DISSEMINATED
                )
                disseminated = None

            # IF THE DISSEMINATION SUCCEEDED
            # `disseminated` is None if there were no errors.
            if disseminated is None:
                # Remove workbook artifacts after the report has been disseminated.
                # We do this outside of the atomic block. No race between
                # two instances of the FAC should be able to get to this point.
                # If we do, something will fail.
                audit_remove_workbook_artifacts(audit)

            # IF THE DISSEMINATION FAILED
            # If disseminated has a value, it is an error
            if disseminated is not None:
                logger.info(
                    "{} is a `not None` value report_id[{}] for `disseminated`".format(
                        report_id, disseminated
                    )
                )

            return redirect(reverse("audit:MySubmissions"))

        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
        except TransactionManagementError:
            # ORIGINAL COMMENT
            # This is most likely the result of a race condition, where the user hits
            # the submit button multiple times and the requests get round-robined to
            # different instances, and the second attempt tries to insert an existing
            # report_id into the dissemination.General table.
            # Our assumption is that the first request succeeded (otherwise there
            # wouldn't be an entry with that report_id to cause the error), and that we
            # should log this but not report it to the user.
            # See https://github.com/GSA-TTS/FAC/issues/3347
            # UPDATED 2024-09-13
            # We have not been able to trigger this error in the most recent race
            # debugging. However, that does not mean it is impossible.
            # Therefore, leaving this exception handler in place.
            logger.info("IntegrityError on disseminating report_id: %s", report_id)
            if (
                Audit.objects.get(report_id=report_id).submission_status
                == STATUS.DISSEMINATED
            ):
                return redirect(reverse("audit:MySubmissions"))
            raise
