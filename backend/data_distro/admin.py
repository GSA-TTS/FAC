from django.apps import apps
from django.contrib import admin


# get all the data_distro models
distro_classes = apps.all_models["data_distro"]

# This is a basic way to  see data_distro models in the admin
for model in distro_classes:
    # You can add custom registration earlier in the file the exception prevents clobbering
    try:
        admin.site.register(distro_classes[model])
    except admin.sites.AlreadyRegistered:
        pass
