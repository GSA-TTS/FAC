import contextvars
from contextlib import contextmanager


current_audit = contextvars.ContextVar("current_audit", default=None)


@contextmanager
def set_audit_to_context(audit):
    reference = current_audit.set(audit)
    try:
        yield
    finally:
        current_audit.reset(reference)


def get_audit_from_context():
    return current_audit.get(None)
