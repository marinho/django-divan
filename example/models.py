from django.db import models
from django_divan.divan.models import BaseOption, CouchModel, OptionChoice

class ExampleOption(BaseOption):
    active = models.BooleanField()

    class Divan:
        database = 'example'
        choice_related_name = 'exampleoptionchoice_set'


class ExampleOptionChoice(OptionChoice):
    option = models.ForeignKey(ExampleOption)


class Example(CouchModel):
    class Divan:
        schema = ExampleOption
        groups = ['meat', 'vegetarian'] 
