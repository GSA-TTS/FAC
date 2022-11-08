from django.views import generic
from .models import Posts


# class based views for posts
class home(generic.TemplateView):
    """Basic class for home."""

    template_name = "home.html"


# class based view for each post
class postdetail(generic.DetailView):
    """Basic details class"""

    model = Posts
    template_name = "post.html"
