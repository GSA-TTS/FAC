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
    SingleAuditChecklist,
    Audit,
    Access,
)
from audit.models.constants import STATUS
from audit.models.utils import generate_audit_indexes
from audit.models.viewflow import sac_transition
from audit.decorators import verify_status

from dissemination.remove_workbook_artifacts import remove_workbook_artifacts
from dissemination.models import General

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
        # TODO SOT: Enable for testing
        # use_audit = request.GET.get("beta", "N") == "Y"
        use_audit = False
        submissions = MySubmissions.fetch_my_submissions(request.user, use_audit)

        data = {"completed_audits": [], "in_progress_audits": []}
        for audit in submissions:
            audit["submission_status"] = _friendly_status(audit["submission_status"])
            if audit["submission_status"] in ["Submitted", "Disseminated"]:
                data["completed_audits"].append(audit)
            else:
                data["in_progress_audits"].append(audit)

        context = {
            "data": data,
            "new_link": new_link,
            "edit_link": edit_link,
            "is_beta": use_audit,
            "non_beta_url": "audit:MySubmissions",
        }
        return render(request, template_name, context)

    @classmethod
    def fetch_my_submissions(cls, user, use_audit):
        """
        Get all submissions the user is associated with via Access objects.
        """
        accesses = Access.objects.filter(user=user)

        # TODO: Update Post SOC Launch
        if use_audit:
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
        else:
            sac_ids = [access.sac.id for access in accesses]
            data = SingleAuditChecklist.objects.filter(
                Q(id__in=sac_ids) & ~Q(submission_status=STATUS.FLAGGED_FOR_REMOVAL)
            ).values(
                "report_id",
                "submission_status",
                auditee_uei=F("general_information__auditee_uei"),
                auditee_name=F("general_information__auditee_name"),
                fiscal_year_end_date=F(
                    "general_information__auditee_fiscal_period_end"
                ),
            )
            return data


class EditSubmission(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        return redirect(reverse("singleauditchecklist", args=[report_id]))


class SubmissionView(CertifyingAuditeeRequiredMixin, generic.View):
    @verify_status(STATUS.AUDITEE_CERTIFIED)
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }

            return render(request, "audit/submission.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.AUDITEE_CERTIFIED)
    def post(self, request, *args, **kwargs):  # noqa: C901
        # RACE HAZARD WARNING
        # It is possible for a user to enter the submission multiple times,
        # from multiple FAC instances. This race hazard is documented in
        # backend/audit/views/README-fac-views-race-hazard-postmortem.md
        report_id = kwargs["report_id"]
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            errors = sac.validate_full()

            # TODO: Update Post SOC Launch
            audit = Audit.objects.find_audit_or_none(report_id=report_id)
            if audit:
                audit_errors = audit.validate()
                _compare_errors(errors, audit_errors)

            if errors:
                context = {"report_id": report_id, "errors": errors}

                return render(
                    request,
                    "audit/cross-validation/cross-validation-results.html",
                    context,
                )

            # TODO: Update Post SOC Launch Atomic stuff should be able to go away.
            # Only change this value if things work...
            disseminated = "DID NOT DISSEMINATE"

            # BEGIN ATOMIC BLOCK
            with transaction.atomic():
                sac_transition(
                    request, sac, audit=audit, transition_to=STATUS.SUBMITTED
                )
                disseminated = sac.disseminate()
                if audit:
                    audit_indexes = generate_audit_indexes(audit)
                    audit.audit.update(audit_indexes)

                # `disseminated` is None if there were no errors.
                if disseminated is None:
                    sac_transition(
                        request, sac, audit=audit, transition_to=STATUS.DISSEMINATED
                    )
            # END ATOMIC BLOCK

            # IF THE DISSEMINATION SUCCEEDED
            # `disseminated` is None if there were no errors.
            if disseminated is None:
                # Remove workbook artifacts after the report has been disseminated.
                # We do this outside of the atomic block. No race between
                # two instances of the FAC should be able to get to this point.
                # If we do, something will fail.
                remove_workbook_artifacts(sac)

            # IF THE DISSEMINATION FAILED
            # If disseminated has a value, it is an error
            # object returned from `sac.disseminate()`
            if disseminated is not None:
                logger.info(
                    "{} is a `not None` value report_id[{}] for `disseminated`".format(
                        report_id, disseminated
                    )
                )

            return redirect(reverse("audit:MySubmissions"))

        except SingleAuditChecklist.DoesNotExist:
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
            if General.objects.get(report_id=sac.report_id):
                return redirect(reverse("audit:MySubmissions"))
            raise


def _friendly_status(status):
    return dict(SingleAuditChecklist.STATUS_CHOICES)[status]


# TODO: Post SOT Launch: Delete
def _compare_errors(sac_errors, audit_errors):
    if (sac_errors and audit_errors) and set(sac_errors) != set(audit_errors):
        logger.error(
            f"<SOT ERROR> Submission Errors do not match: SAC {sac_errors}, Audit {audit_errors}"
        )
