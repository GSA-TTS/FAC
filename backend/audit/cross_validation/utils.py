import random


def generate_random_integer(min, max):
    """Generate a random integer between min and max."""
    return random.randint(min, max)  # nosec


def check_inclusion(A, B):
    """Check if A is a subset of B. If not, return the list of items in set A that do not belong to set B."""
    difference = A - B
    if difference:
        return False, list(difference)
    return True, []
