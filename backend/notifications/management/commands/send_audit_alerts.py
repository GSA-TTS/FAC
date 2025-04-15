from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from datetime import datetime, timedelta
import requests
from notifications.models import Subscriber

API_KEY = "YMOPUA7oUlWM0hl27MzVuaRfSeybQQAcK7yOi6It"
FAC_API_URL = "https://api.fac.gov/general"

class Command(BaseCommand):
    help = "Send audit submission notifications to subscribers"

    def handle(self, *args, **kwargs):
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        full_url = f"{FAC_API_URL}?submitted_date=gte.{yesterday}&submitted_date=lte.{today}"
        headers = {"X-API-Key": API_KEY}

        try:
            response = requests.get(full_url, headers=headers)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"API request failed: {e}"))
            return

        if not data:
            self.stdout.write("No new audits found.")
            return

        subscribers = Subscriber.objects.filter(frequency="daily")

        for sub in subscribers:
            body = "\n".join([
                f"{entry['auditee_name']} - {entry['submitted_date']} - Report ID: {entry['report_id']} - "
                f"COG: {entry.get('cognizant_agency', 'N/A')} / OVER: {entry.get('oversight_agency', 'N/A')}"
                for entry in data
                
            ])
            unsubscribe_url = f"http://localhost:8000/notifications/unsubscribe/{sub.unsubscribe_token}/"
            body += f"\n\nTo unsubscribe from these alerts, click here: {unsubscribe_url}"

            send_mail(
                subject="FAC: New Audit Submissions",
                message=body,
                from_email="noreply@fac.gov",
                recipient_list=[sub.email],
            )

            sub.last_sent = datetime.utcnow()
            sub.save()

        self.stdout.write(f"Email sent to {subscribers.count()} subscribers.")
