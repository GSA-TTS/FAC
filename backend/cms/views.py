from .models import Posts
from django.views import generic
from django.shortcuts import render

# class based views for posts


class home(generic.View):
    def get(self, request, *args, **kwargs):
        template_name = "home.html"
        if request.user.is_authenticated:
            template_name = "audit/my_submissions.html"
        return render(request, template_name)


# class based view for each post
class postdetail(generic.DetailView):
    """Basic details class"""

    model = Posts
    template_name = "post.html"
