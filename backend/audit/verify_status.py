import logging

from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

from audit.models import SingleAuditChecklist


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


def verify_status(status):
    """
    Decorator to be applied to view request methods (i.e. get, post) to verify
    that the submission is in the correct state before allowing the user to
    proceed. An incorrect status usually happens via direct URL access. If the
    given status(es) do(es) not match the submission's, it will redirect them back to
    the submission progress page. Accepts either a str or a [str].
    """
    def decorator_verify_status(request_method):
        def verify(view, request, *args, **kwargs):
            report_id = kwargs["report_id"]

            try:
                sac = SingleAuditChecklist.objects.get(report_id=report_id)
            except SingleAuditChecklist.DoesNotExist:
                raise PermissionDenied("You do not have access to this audit.")

            statuses = status if type(status) == list else [status]

            if sac.submission_status not in statuses:
                # Return to checklist, the audit is not in the correct state
                logger.warning(
                    f"Expected submission status {status} but it's currently {sac.submission_status}"
                )
                return redirect(f"/audit/submission-progress/{sac.report_id}")
            else:
                return request_method(view, request, *args, **kwargs)

        return verify

    return decorator_verify_status
