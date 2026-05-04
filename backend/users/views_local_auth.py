from django.contrib.auth import logout
from django.shortcuts import redirect

def local_logout(request):
    logout(request)
    return redirect("/")
