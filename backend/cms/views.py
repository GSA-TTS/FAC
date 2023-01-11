from .models import Posts
from django.views import generic
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse


# class based views for posts
class Home(generic.View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            url = reverse("MySubmissions")
            return redirect(url)
        template_name = "home.html"
        extra_context = {}
        return render(request, template_name, extra_context)


# class based view for each post
class postdetail(generic.DetailView):
    """Basic details class"""

    model = Posts
    template_name = "post.html"


# robots.txt
def NoRobots(context):
    content = "User-agent: *\nDisallow: /"
    return HttpResponse(content, content_type="text/plain")
