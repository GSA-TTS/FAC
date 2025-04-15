from django.db import models
import uuid

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    frequency = models.CharField(
        max_length=10,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly')],
        blank=True
    )
    subscribed_on = models.DateTimeField(auto_now_add=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    unsubscribe_token = models.UUIDField(blank=True, null=True, editable=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.unsubscribe_token:
            self.unsubscribe_token = uuid.uuid4()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email