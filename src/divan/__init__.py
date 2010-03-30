from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

try:
    DIVAN_BACKEND = getattr(settings, 'DIVAN_BACKEND')
except AttributeError:
    raise ImproperlyConfigured('No Divan backend declared')

module, backend_class_name = DIVAN_BACKEND.rsplit('.', 1)
mod = import_module(module)
backend_class = getattr(mod, backend_class_name)

DIVAN_HOST = getattr(settings, 'DIVAN_HOST', backend_class.default_host)
DIVAN_PORT = getattr(settings, 'DIVAN_PORT', backend_class.default_port)

try:
    DIVAN_DATABASE = getattr(settings, 'DIVAN_DATABASE')
except AttributeError:
    raise ImproperlyConfigured('No Divan database declared')

db = backend_class(DIVAN_DATABASE, DIVAN_HOST, DIVAN_PORT)
