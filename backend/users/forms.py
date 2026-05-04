from django import forms
from .models import EmailSubscription

class EmailSubscriptionForm(forms.ModelForm):
    class Meta:
        model = EmailSubscription
        fields = ['email']
        labels = {'email': 'Subscribe to daily email alerts'}
