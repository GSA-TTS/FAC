"""Test management commands."""

import logging

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from audit.models import SingleAuditChecklist


class TestLoadFixturesCommand(TestCase):
    def test_load_fixtures(self):
        """load_fixtures command makes some single audit checklists."""
        # make sure we have at least one user
        User = get_user_model()
        User.objects.get_or_create(username="test_at_least_one")

        # we want to check logs so undo the log level override from
        # settings.py when we are testing:
        logging.disable(logging.NOTSET)

        with self.assertLogs(
            logger="audit.fixtures.single_audit_checklist", level="DEBUG"
        ) as logs:
            call_command("load_fixtures")
        self.assertTrue(
            any("test_at_least_one" in log_line for log_line in logs.output)
        )
        self.assertTrue(
            SingleAuditChecklist.objects.filter(
                submitted_by__username="test_at_least_one"
            ).exists()
        )

        # restore the logging override
        logging.disable(logging.ERROR)
