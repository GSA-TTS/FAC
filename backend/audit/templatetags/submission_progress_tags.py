"""
Custom tag to support the logic around sections on the Submission progress page.
"""
from django import template

register = template.Library()


@register.inclusion_tag("section_block.html")
def section_block(report_id, section_info):
    """
    Returns the context dict that the above template will use.
    Most of the work for this is done in
    cross_validation.submission_progress_check.progress_check, because that's a
    little more centralized and troubleshooting is a little easier if the work is done before
    template rendering rather than during.
    """
    additional_info = {
        "report_id": report_id,
    }
    title = section_info["friendly_title"]
    if workbook_number := section_info["workbook_number"]:
        title = f"Upload Workbook {workbook_number}: {title}"
    if section_info.get("completed") is True:
        title = f"{title} (Complete)"
    additional_info["title"] = title
    additional_info["ctx"] = section_info
    return section_info | additional_info


"""
python manage.py test audit.test_submission_progress_view
python manage.py shell
from audit.templatetags.submission_progress_tags import section_block as sb
sb('whatever', {}, "general_information")
from audit.cross_validation.sac_validation_shape import get_shaped_section
from audit.models import SingleAuditChecklist
sac = SingleAuditChecklist.objects.get(id=2)
"""
