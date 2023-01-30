from django.apps import apps
from django.contrib import admin

# can add custom registration here
# admin.site.register(model)

# get all the data_distro models
distro_classes = apps.all_models["data_distro"]

# TODO: register models properly, I just want to iterate on models and see them in the admin for now
for model in distro_classes:
    try:
        admin.site.register(distro_classes[model])
    except admin.sites.AlreadyRegistered:
        pass
