from django.db import models
from divan.models import BaseOption, DivanModel, OptionChoice

class ExampleOption(BaseOption):
    active = models.BooleanField()

    class Divan:
        database = 'example'
        choice_related_name = 'exampleoptionchoice_set'


class ExampleOptionChoice(OptionChoice):
    option = models.ForeignKey(ExampleOption)


class Example(DivanModel):
    class Divan:
        schema = ExampleOption
        groups = ['meat', 'vegetarian'] 
