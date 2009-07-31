from django.db import models
from django_divan.divan.models import BaseOption

class ExampleOption(BaseOption):
    active = models.BooleanField()
