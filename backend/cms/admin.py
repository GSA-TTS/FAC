from django.contrib import admin

from .models import Posts


class PostAdmin(admin.ModelAdmin):
    fields = ["title", "slug", "author", "meta_description", "content"]


admin.site.register(Posts, PostAdmin)
