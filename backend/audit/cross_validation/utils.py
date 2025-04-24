import random


def generate_random_integer(min, max):
    """Generate a random integer between min and max."""
    return random.randint(min, max)  # nosec


def format_refs(ref_set: set) -> str:
    """Format a set of references as a comma-separated string."""
    return ", ".join(sorted(ref_set))


def make_findings_uniform_guidance(refs, auditee_uei) -> dict:
    return {
        "findings_uniform_guidance": [
            {"findings": {"reference_number": ref}} for ref in refs
        ]
    }
