from django.forms import model_to_dict

from model_bakery import baker

from dissemination.models import (
    Unified,
)


def bake_unified(gen_obj, other_objs=[]):
    """
    Bakes a Unified object given a General object and optional FederalAward,
    Passthrough, and Finding objects
    """
    uni = model_to_dict(gen_obj)

    for other_obj in other_objs:
        uni.update(model_to_dict(other_obj))

    uni["report_id"] = gen_obj

    return baker.make(Unified, **uni)
