from audit.models import SingleAuditChecklist, User, SubmissionEvent
from audit.models.viewflow import SingleAuditChecklistFlow
from curation.curationlib.curation_audit_tracking import CurationTracking

import logging
import sys
from django.db.models import Q
from django.db import transaction

from dissemination.models import _dissemination_models

logger = logging.getLogger(__name__)


# FIXME: Should this be added to `naming.py`
# so we can take a name and convert it to a model?
def get_named_models():
    return _dissemination_models


def status_to_bool(s):
    if str(s).lower() in ["y", "yes", "true", True]:
        return True
    if str(s).lower() in ["n", "no", "false", False]:
        return False
    else:
        raise Exception("Failing hard because of bad boolean conversion.")


def get_named_parts_containing_ueis(sac):
    return {
        "AdditionalEINs": sac.additional_eins,
        "AdditionalUEIs": sac.additional_ueis,
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
    except SingleAuditChecklist.DoesNotExist:
        return False


# options hash -> Django queryset
def get_sac_with_uei(options):
    # Note that the UEI is not only in the general info, but
    # also in every one of the workbooks. Too bad we stored it that way.
    crit1 = Q(report_id=options["report_id"])
    crit2 = Q(general_information__auditee_uei=options["old_uei"])
    crit3 = Q(submission_status="disseminated")
    # We already validated that there will only be one object coming back.
    sac = SingleAuditChecklist.objects.get(crit1 & crit2 & crit3)
    return sac


# options hash -> Django queryset
def get_sac_with_ein_to_update(options):
    # Does the old EIN exist?
    crit1 = Q(report_id=options["report_id"])
    crit2 = Q(general_information__ein=options["old_ein"])
    crit3 = Q(submission_status="disseminated")
    sac = SingleAuditChecklist.objects.get(crit1 & crit2 & crit3)
    return sac


# options hash -> Django queryset
def get_sac_with_report_id(options):
    crit1 = Q(report_id=options["report_id"])
    crit2 = Q(submission_status="disseminated")
    sac = SingleAuditChecklist.objects.get(crit1 & crit2)
    return sac


def update_db(sac, THE_USER_OBJ, event_type):
    # If curation tracking is enabled *inside* of an atomic block
    # it blocks when we try and disable it. I think (without evidence)
    # that is because we enable and disable triggers as part of this
    # process, and I suspect that does not work (to enable *and* disable)
    # while in a BEGIN/transaction.
    with CurationTracking():
        with transaction.atomic():
            flow = SingleAuditChecklistFlow(sac)
            flow.transition_via_redissemination()
            sac.save(
                administrative_override=True,
                event_user=THE_USER_OBJ,
                event_type=event_type,
            )
            sac.redisseminate()


def update_uei(options):
    # If we get here, the parameters validated.
    # Now we need to pull the SAC, update the record, and
    # save the new UEI.
    THE_NEW_UEI = options["new_uei"]
    sac = get_sac_with_uei(options)
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
                logger.error(
                    f"Could not find auditee_uei in XLSX JSON object {json_field}"
                )
                sys.exit(-1)

    logger.info("Updating UEI for SAC: " + str(sac))
    update_db(
        sac,
        THE_USER_OBJ,
        SubmissionEvent.EventType.FAC_ADMINISTRATIVE_UEI_REPLACEMENT,
    )


def update_ein(options):
    # Now we need to pull the SAC, update the record, and
    # save the new EIN.
    THE_NEW_EIN = options["new_ein"]

    # The EIN is only in the general info.
    sac = get_sac_with_ein_to_update(options)

    THE_USER_OBJ = User.objects.get(email=options["email"])

    sac.general_information["ein"] = THE_NEW_EIN

    logger.info("Updating EIN for SAC: " + str(sac))
    update_db(
        sac,
        THE_USER_OBJ,
        SubmissionEvent.EventType.FAC_ADMINISTRATIVE_EIN_REPLACEMENT,
    )


# JSON fields
# is_tribal_information_authorized_to_be_public
# tribal_authorization_certifying_official_name
# tribal_authorization_certifying_official_title
def update_authorized_public(options):
    sac = get_sac_with_report_id(options)
    if sac.tribal_data_consent is None:
        logger.error(
            "It is not possible to update the consent of a record without an existing attestation."
        )
        sys.exit(-1)
    else:
        current_status = status_to_bool(
            sac.tribal_data_consent["is_tribal_information_authorized_to_be_public"]
        )

    new_status = status_to_bool(options["new_authorization"])

    logger.info(f"current authorized to be public: {current_status} new: {new_status}")

    THE_USER_OBJ = User.objects.get(email=options["email"])

    # Change the status
    # Try and keep the original certifying name, but annotate it.
    # If it is currently authorized to be public (true), and we want to suppress it (false),
    # we need to add a new, fake consent that says it may not be public.
    if current_status and not new_status:
        certification = {
            "is_tribal_information_authorized_to_be_public": False,
        }

    # If it is currently not authorized to be public (false) and we want to make
    # it public (true), then we need to set the cert to True.
    if not current_status and new_status:
        certification = {
            "is_tribal_information_authorized_to_be_public": True,
        }

    name = sac.tribal_data_consent["tribal_authorization_certifying_official_name"]
    title = sac.tribal_data_consent["tribal_authorization_certifying_official_title"]
    suffix = "/FAC"
    if suffix not in name:
        name = name + suffix
    if suffix not in title:
        title = title + suffix
    certification["tribal_authorization_certifying_official_name"] = name
    certification["tribal_authorization_certifying_official_title"] = title

    # Set the object
    sac.tribal_data_consent = certification
    # Save it.
    logger.info("Updating suppression for: " + str(sac))
    update_db(
        sac,
        THE_USER_OBJ,
        SubmissionEvent.EventType.FAC_ADMINISTRATIVE_SUPPRESSION_CHANGE,
    )
    return True
