from divan.forms import DivanForm
from testproject.example.models import ExampleOption

class ExampleOptionForm(DivanForm):
    class Divan:
        model = ExampleOption
