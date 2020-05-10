from django.contrib.admin import ModelAdmin
from django.db import models
from django.forms import widgets


class BaseAdmin(ModelAdmin):
    formfield_overrides = {models.TextField: {'widget': widgets.TextInput}}
