import re
import os
import sys
import glob
import warnings
from itertools import dropwhile
from optparse import make_option

from django.conf import settings
from django.core.management.base import CommandError, BaseCommand
from django.db import models

from divan.models import BaseOption, OptionModelBase

try:
    set
except NameError:
    from sets import Set as set     # For Python 2.3

# Intentionally silence DeprecationWarnings about os.popen3 in Python 2.6. It's
# still sensible for us to use it, since subprocess didn't exist in 2.3.
warnings.filterwarnings('ignore', category=DeprecationWarning, message=r'os\.popen3')

DEFAULT_DIVAN_SERVER = getattr(settings, 'DEFAULT_DIVAN_SERVER', 
        'http://localhost:5984/')

def make_messages(locale=None, verbosity=1, fieldstrings='all'):
    """
    Uses the locale directory from the Django SVN tree or an application/
    project to process all
    """
    # Need to ensure that the i18n framework is enabled
    from django.conf import settings
    if settings.configured:
        settings.USE_I18N = True
    else:
        settings.configure(USE_I18N = True)

    if os.path.isdir(os.path.join('conf', 'locale')):
        localedir = os.path.abspath(os.path.join('conf', 'locale'))
    elif os.path.isdir('locale'):
        localedir = os.path.abspath('locale')
    else:
        raise CommandError("This script should be run from your project or app tree. If you did indeed run it from your project or application, maybe you are just missing the locale directory? It is not created automatically, you have to create it by hand if you want to enable i18n for your project or application.")

    # xgettext versions prior to 0.15 assumed Python source files were encoded
    # in iso-8859-1, and produce utf-8 output.  In the case where xgettext is
    # given utf-8 input (required for Django files with non-ASCII characters),
    # this results in a utf-8 re-encoding of the original utf-8 that needs to be
    # undone to restore the original utf-8.  So we check the xgettext version
    # here once and set a flag to remember if a utf-8 decoding needs to be done
    # on xgettext's output for Python files.  We default to assuming this isn't
    # necessary if we run into any trouble determining the version.
    xgettext_reencodes_utf8 = False
    domain = 'django'
    (stdin, stdout, stderr) = os.popen3('xgettext --version', 't')
    match = re.search(r'(?P<major>\d+)\.(?P<minor>\d+)', stdout.read())
    if match:
        xversion = (int(match.group('major')), int(match.group('minor')))
        if xversion < (0, 15):
            xgettext_reencodes_utf8 = True
 
    languages = []
    if locale is not None:
        languages.append(locale)
    else:
        locale_dirs = filter(os.path.isdir, glob.glob('%s/*' % localedir)) 
        languages = [os.path.basename(l) for l in locale_dirs]
    
    for locale in languages:
        if verbosity > 0:
            print "processing language", locale
        basedir = os.path.join(localedir, locale, 'LC_MESSAGES')
        if not os.path.isdir(basedir):
            os.makedirs(basedir)

        pofile = os.path.join(basedir, '%s.po' % domain)
        potfile = os.path.join(basedir, '%s.pot' % domain)

        if os.path.exists(potfile):
            os.unlink(potfile)

        field_names = []
        help_text = []
        values = []
        for app in models.get_apps():
            app_name = app.__name__.split('.')[-2]
            model_list = models.get_models(app)
            for model in model_list:
                if model.__metaclass__.__name__ == 'OptionModelBase':
                    print "Processing %s.%s model" % (app_name, model._meta.object_name)
                    db = model.couchdb()
                    for field in model.objects.all():
                        if fieldstrings in ('fieldnames', 'all'):
                            field_names.append(field.field_name)
                        if fieldstrings in ('helptext', 'all'):
                            help_text.append(field.help_text)
                        if field.field_type == 'CharField' and fieldstrings in ('values', 'all'):
                            query_func = "function (doc) { if (doc.%s) { emit(doc.%s, null); }}" % (field.key, field.key)
                            results = db.query(query_func)
                            values.extend(row.key for row in results)
        strings = field_names + help_text + values
        string_blob = '\\n'.join(list(set("\'%s\'" % s.replace("'", "\\'") for s in strings if s)))
        cmd = """echo "%s" | xgettext -d %s -L Python -a --keyword=gettext_noop --keyword=gettext_lazy --keyword=ngettext_lazy:1,2 --keyword=ugettext_noop --keyword=ugettext_lazy --keyword=ungettext_lazy:1,2 --from-code UTF-8 -o - -""" % (
            string_blob, domain) 
        (stdin, stdout, stderr) = os.popen3(cmd, 't')
        msgs = stdout.read()
        errors = stderr.read()
        if errors:
            raise CommandError("errors happened while running xgettext on %s\n%s" % (file, errors))

        if xgettext_reencodes_utf8:
            msgs = msgs.decode('utf-8').encode('iso-8859-1')

        if os.path.exists(potfile):
            # Strip the header
            msgs = '\n'.join(dropwhile(len, msgs.split('\n')))
        else:
            msgs = msgs.replace('charset=CHARSET', 'charset=UTF-8')
        if msgs:
            open(potfile, 'ab').write(msgs)

        if os.path.exists(potfile):
            (stdin, stdout, stderr) = os.popen3('msguniq --to-code=utf-8 "%s"' % potfile, 't')
            msgs = stdout.read()
            errors = stderr.read()
            if errors:
                raise CommandError("errors happened while running msguniq\n%s" % errors)
            open(potfile, 'w').write(msgs)
            if os.path.exists(pofile):
                (stdin, stdout, stderr) = os.popen3('msgmerge -q "%s" "%s"' % (pofile, potfile), 't')
                msgs = stdout.read()
                errors = stderr.read()
                if errors:
                    raise CommandError("errors happened while running msgmerge\n%s" % errors)
            open(pofile, 'wb').write(msgs)
            os.unlink(potfile)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--locale', '-l', default=None, dest='locale',
            help='Creates or updates the message files only for the given locale (e.g. pt_BR).'),
        make_option('--fieldstrings', '-f', default=None, dest='locale',
            help='Determines what strings are pulled from the Divan database. Options: "all", "helptext", "fieldnames", "values"'),
    )
    help = "Creates/updates .po files for BaseOption subclass strings and all Divan documents with matching keys."

    requires_model_validation = False
    can_import_settings = False

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")

        locale = options.get('locale')
        fieldstrings = options.get('fieldstrings', 'all')
        verbosity = int(options.get('verbosity'))
        make_messages(locale, verbosity, fieldstrings)

