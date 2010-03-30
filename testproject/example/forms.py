from django_divan.divan.forms import DivanForm
from django_divan.example.models import ExampleOption

class ExampleOptionForm(DivanForm):
    class Divan:
        model = ExampleOption
