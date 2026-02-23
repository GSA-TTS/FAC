import contextvars
from contextlib import contextmanager

current_sac = contextvars.ContextVar("current_sac", default=None)


@contextmanager
def set_sac_to_context(sac):
    reference = current_sac.set(sac)
    try:
        yield
    finally:
        current_sac.reset(reference)


def get_sac_from_context():
    return current_sac.get(None)
