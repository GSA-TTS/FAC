import random


def generate_random_integer(min, max):
    """Generate a random integer between min and max."""
    return random.randint(min, max)  # nosec


def format_refs(ref_set: set) -> str:
    """Format a set of references as a comma-separated string."""
    return ", ".join(sorted(ref_set))


def make_findings_uniform_guidance(refs, auditee_uei) -> dict:
    entries = []
    for ref in refs:
        entries.append({"findings": {"reference_number": ref}})

    findings = (
        {
            "auditee_uei": auditee_uei,
            "findings_uniform_guidance_entries": entries,
        }
        if len(entries) > 0
        else {"auditee_uei": auditee_uei}
    )

    return {"FindingsUniformGuidance": findings}
