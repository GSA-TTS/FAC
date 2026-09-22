from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.formats import date_format

"""
This model is used to determine if an maintenance banner should be displayed in
the app. It can be enabled/disabled manually, or optional start/end times can
be provided for automatic handling. This is a singleton model, so it's
restricted to a single row that is updated as needed.
"""


class MaintenanceBanner(models.Model):
    is_active = models.BooleanField(
        default=False,
        help_text="Master toggle to enable or disable the banner",
    )
    message = models.TextField(
        max_length=500,
        blank=True,
        help_text="Optional custom message. If left blank, a default "
        "maintenance message will be generated using start and end times.",
    )
    start_time = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the banner should start showing (optional)",
    )
    end_time = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the banner should stop showing (optional)",
    )
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def display_message(self):
        """
        Returns the explicit message if set; otherwise generates a default message
        """
        if self.message:
            return self.message
        elif self.start_time and self.end_time:
            start_str = date_format(
                timezone.localtime(self.start_time), "N j, Y, g:i a"
            )
            end_str = date_format(timezone.localtime(self.end_time), "N j, Y, g:i a e")
            return (
                f"FAC.gov will be performing maintenance from {start_str} to {end_str}. "
                f"During this period, the entire website will be unavailable."
            )
        else:
            return "FAC.gov is currently performing maintenance. Some services may be unavailable."

    @property
    def is_currently_active(self):
        """
        Returns true when the master toggle and schedule determine the banner to
        be active
        """
        if not self.is_active:
            return False

        now = timezone.now()

        if self.start_time and now < self.start_time:
            return False

        if self.end_time and now > self.end_time:
            return False

        return True

    def clean(self):
        # Enforces singleton model
        if not self.pk and MaintenanceBanner.objects.exists():
            raise ValidationError(
                "Only one Maintenance Banner instance is allowed. Please edit the existing one.",
            )

        # Validates scheduling logic
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({"end_time": "End time must be after start time."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Maintenance Banner ({'Active' if self.is_currently_active else 'Inactive'})"
