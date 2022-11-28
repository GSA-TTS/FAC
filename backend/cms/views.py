from django.views import generic
from .models import Posts


# class based views for posts
class postslist(generic.ListView):
    """Basic list class"""

    queryset = Posts.objects.order_by("-created_on")
    template_name = "home.html"
    paginate_by = 4


# class based view for each post
class postdetail(generic.DetailView):
    """Basic details class"""

    model = Posts
    template_name = "post.html"
