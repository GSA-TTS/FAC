# importing django models and users
from django.db import models
from django.contrib.auth.models import User



# creating an django model class
class Posts(models.Model):
    # title field using charfield constraint with unique constraint
    title = models.CharField(max_length=200, unique=True)
    # slug field auto populated using title with unique constraint
    slug = models.SlugField(max_length=200, unique=True)
    # author field populated using users database
    author = models.ForeignKey(User, on_delete= models.CASCADE)
    # and date time fields automatically populated using system time
    updated_on = models.DateTimeField(auto_now= True)
    created_on = models.DateTimeField(auto_now_add=True)
    # content field to store our post
    content = models.TextField()
    # meta description for SEO benefits and accessibility
    meta_description = models.CharField(max_length=300, null=True)


    # meta for the class
    class Meta:
        ordering = ['-created_on']
    # used while managing models from terminal
    def __str__(self):
        return self.title
