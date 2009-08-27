from django_divan.divan.forms import CouchForm
from django_divan.example.models import ExampleOption

class ExampleOptionForm(CouchForm):
    class Divan:
        model = ExampleOption
