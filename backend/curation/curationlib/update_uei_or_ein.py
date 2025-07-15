from django.core.management.base import BaseCommand

from audit.models import SingleAuditChecklist, User, SubmissionEvent
import logging
import sys
from django.db.models import Q
from django.db import transaction

from dissemination.models import (
    AdditionalEin,
    AdditionalUei,
    CapText,
    FederalAward,
    Finding,
    FindingText,
    General,
    Note,
    Passthrough,
    SecondaryAuditor,
)


logger = logging.getLogger(__name__)


# FIXME: Should this be added to `naming.py`
# so we can take a name and convert it to a model?
def get_named_models():
    return {
        "AdditionalEins": AdditionalEin,
        "AdditionalUeis": AdditionalUei,
        "CorrectiveActionPlan": CapText,
        "FederalAwards": FederalAward,
        "FindingsText": FindingText,
        "FindingsUniformGuidance": Finding,
        "NotesToSefa": Note,
        "SecondaryAuditors": SecondaryAuditor,
        "General": General,
        "Passthrough": Passthrough,
    }


def get_named_parts_containing_ueis(sac):
    return {
        "AdditionalEins": sac.additional_eins,
        "AdditionalUeis": sac.additional_ueis,
        "CorrectiveActionPlan": sac.corrective_action_plan,
        "FederalAwards": sac.federal_awards,
        "FindingsText": sac.findings_text,
        "FindingsUniformGuidance": sac.findings_uniform_guidance,
        "NotesToSefa": sac.notes_to_sefa,
        "SecondaryAuditors": sac.secondary_auditors,
    }


def check_report_disseminated(options):
    crit1 = Q(report_id=options["report_id"])
    crit3 = Q(submission_status="disseminated")
    try:
        _ = SingleAuditChecklist.objects.get(crit1 & crit3)
        return True
    except:
        return False


# options hash -> Django queryset
def get_uei_to_update(options):
    # Note that the UEI is not only in the general info, but
    # also in every one of the workbooks. Too bad we stored it that way.
    crit1 = Q(report_id=options["report_id"])
    crit2 = Q(general_information__auditee_uei=options["old_uei"])
    crit3 = Q(submission_status="disseminated")
    # We already validated that there will only be one object coming back.
    sac = SingleAuditChecklist.objects.get(crit1 & crit2 & crit3)
    return sac


# options hash -> Django queryset
def get_ein_to_update(options):
    # Does the old EIN exist?
    crit1 = Q(report_id=options["report_id"])
    crit2 = Q(general_information__ein=options["old_ein"])
    crit3 = Q(submission_status="disseminated")
    sac = SingleAuditChecklist.objects.get(crit1 & crit2 & crit3)
    return sac


def update_uei(options):
    # If we get here, the parameters validated.
    # Now we need to pull the SAC, update the record, and
    # save the new UEI.
    THE_NEW_UEI = options["new_uei"]
    sac = get_uei_to_update(options)
    named_parts = get_named_parts_containing_ueis(sac)

    THE_USER_OBJ = User.objects.get(email=options["email"])

    sac.general_information["auditee_uei"] = THE_NEW_UEI
    for json_field, object in named_parts.items():
        # We might not have this workbook.
        if object:
            # If we do have the workbook, we MUST have auditee_uei as a field.
            if json_field in object:
                object[json_field]["auditee_uei"] = THE_NEW_UEI
            else:
                logger.error("Could not find auditee_uei in XLSX JSON object")
                sys.exit(-1)

    with transaction.atomic():
        logger.info("Updating UEI for SAC: " + str(sac))
        sac.save(
            administrative_override=True,
            event_user=THE_USER_OBJ,
            event_type=SubmissionEvent.EventType.FAC_ADMINISTRATIVE_UEI_REPLACEMENT,
        )
        sac.redisseminate()
        return True

    return False


def update_ein(options):
    # print("NEW_EIN", options)
    # Now we need to pull the SAC, update the record, and
    # save the new EIN.
    THE_NEW_EIN = options["new_ein"]

    # The EIN is only in the general info.
    sac = get_ein_to_update(options)

    THE_USER_OBJ = User.objects.get(email=options["email"])

    sac.general_information["ein"] = THE_NEW_EIN

    with transaction.atomic():
        logger.info("Updating EIN for SAC: " + str(sac))
        sac.save(
            administrative_override=True,
            event_user=THE_USER_OBJ,
            event_type=SubmissionEvent.EventType.FAC_ADMINISTRATIVE_EIN_REPLACEMENT,
        )
        sac.redisseminate()
        return True
    return False
