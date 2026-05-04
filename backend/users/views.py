from django.shortcuts import render, redirect
from .forms import EmailSubscriptionForm
from django.http import HttpResponseServerError

def subscribe_view(request):
    try:
        if request.method == "POST":
            form = EmailSubscriptionForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("subscription_success")
        else:
            form = EmailSubscriptionForm()
        return render(request, "users/subscribe.html", {"form": form})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return HttpResponseServerError("Something went wrong. Check the console.")

def subscribe_thanks_view(request):
    return render(request, 'users/subscribe_thanks.html')
