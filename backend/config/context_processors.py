from config import settings


def omb_num_exp_date(request):
    """
    Returns the OMB_NUMBER (str) and OMB_EXP_DATE (str) in template context form.
    Displayed as a legal requirement on the header of every page.
    """
    return {"OMB_NUMBER": settings.OMB_NUMBER, "OMB_EXP_DATE": settings.OMB_EXP_DATE}
