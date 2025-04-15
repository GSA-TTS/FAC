from django.shortcuts import render, redirect
from .forms import SubscriberForm

def subscribe(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'notifications/thank_you.html')
    else:
        form = SubscriberForm()
    return render(request, 'notifications/subscribe.html', {'form': form})

from django.shortcuts import get_object_or_404, render, redirect
from .models import Subscriber

def unsubscribe(request, token):
    subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)

    if request.method == "POST":
        subscriber.delete()
        return render(request, "notifications/unsubscribed.html")

    return render(request, "notifications/unsubscribe_confirm.html", {"subscriber": subscriber})

