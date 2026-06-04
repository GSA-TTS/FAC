def check_test_warning(sac_dict, *_args, **_kwargs):
    """
    A test/demonstration validator that always returns a warning.

    Warnings do not prevent a submission from proceeding; they are shown to
    the user so they can confirm the submission is correct before finalizing.

    This validator should be removed or replaced with a real warning
    validator once the warning pipeline has been confirmed to work end-to-end.

    Returns a list containing a single warning dict.
    """
    return [
        {
            "warning": (
                "This is a test warning. Warnings do not prevent submission. "
                "Please verify your data before proceeding."
            )
        }
    ]
