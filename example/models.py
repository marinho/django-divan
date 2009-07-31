from django.db import models
from django_divan.divan.models import BaseOption, CouchModel

class ExampleOption(BaseOption):
    active = models.BooleanField()


class Example(CouchModel):
    class Meta:
        database = 'example'
        schema = ExampleOption
