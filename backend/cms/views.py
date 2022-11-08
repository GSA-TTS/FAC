from .models import Posts
from django.views import generic


# class based views for posts
class home(generic.TemplateView):
    template_name = 'home.html'


# class based view for each post
class postdetail(generic.DetailView):
    model = Posts
    template_name = "post.html"
