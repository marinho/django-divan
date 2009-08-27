import re
from datetime import date, datetime, time

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from couchdb import Server, client
from divan.timestamps import from_timestamp

DEFAULT_COUCH_SERVER = getattr(settings, 'DEFAULT_COUCH_SERVER', 'http://localhost:5984/')

class OptionModelBase(models.base.ModelBase):
    def __init__(cls, name, bases, attrs):
        opts = getattr(cls, 'Divan', None)
        setattr(cls, '_divan', opts)


class BaseOption(models.Model):
    __metaclass__ = OptionModelBase

    FIELD_TYPE_OPTIONS = (
        ('CharField', 'Text'),
        ('IntegerField', 'Integer'),
        ('FloatField', 'Decimal'),
        ('DateField', 'Date'),
        ('TimeField', 'Time'),
        ('DateTimeField', 'Date and time'),
        ('EmailField', 'E-mail address'),
        ('FileField', 'File'),
        ('ImageField', 'Image file'),
        ('URLField', 'URL'),
        ('BooleanField', 'Checkbox'),
        ('IPAddressField', 'IP address'),
    )
    key = models.CharField(max_length=255, editable=False)
    field_name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=255, choices=FIELD_TYPE_OPTIONS)
    group = models.CharField(max_length=255, blank=True, default='')
    order = models.IntegerField(editable=False)
    help_text = models.TextField(blank=True)
    required = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ('group', 'order',)

    def __unicode__(self):
        return '%s (%s)' % (self.field_name, self.get_field_type_display())

    def save(self, *args, **kwargs):
        if not self.id:
            self.key = re.sub(r'(\W+)', r'_', self.field_name.lower())
            try:
                self.order = self.__class__.objects.order_by('-order')[0].order + 1
            except IndexError:
                self.order = 1
        super(BaseOption, self).save(*args, **kwargs)

    @classmethod
    def couchdb(self):
        server_address = getattr(self._divan, 'server', None) or DEFAULT_COUCH_SERVER
        server = Server(server_address)
        db_name = getattr(self._divan, 'database', None) or settings.DEFAULT_COUCH_DATABASE
        try:
            database = server[db_name]
        except client.ResourceNotFound:
            database = server.create(db_name)
        return database


class CouchModelMetaclass(type):
    def __new__(cls, name, bases, dict):
        new_class = super(CouchModelMetaclass, cls).__new__(cls, name, bases, dict)
        opts = getattr(new_class, 'Divan', None)
        if opts is not None:
            new_class._divan = opts() 
            server_address = getattr(opts, 'server', None) or DEFAULT_COUCH_SERVER
            server = Server(server_address)
            db_name = getattr(opts.schema._divan, 'database', None) or settings.DEFAULT_COUCH_DATABASE
            for f in ('DateField', 'DateTimeField', 'TimeField'):
                if not hasattr(new_class._divan, f):
                    setattr(new_class._divan, f, from_timestamp)
            try:
                new_class.database = server[db_name]
            except client.ResourceNotFound:
                new_class.database = server.create(db_name)
        return new_class


class CouchField(object):
    def __init__(self, val, label):
        self.value = val
        self.label = label

    def __unicode__(self):
        return unicode(self.value)


class BaseCouchModel(object):
    def __init__(self, document_id, **kwargs):
        self.doc = self.database[document_id]
        model = self._divan.schema
        self.groups = {}
        self.fields = []
        for field in model.objects.order_by('group', 'order'):
            group = field.group
            if not self.groups.has_key(group):
                self.groups[field.group] = []
            try:
                val = self.doc[field.key]
            except KeyError:
                continue
            cls_name = field.field_type 
            divan = self._divan
            print cls_name, divan
            if hasattr(divan, cls_name) and val:
                func = getattr(divan, cls_name)
                val = func(val)
            setattr(self, field.key, val)
            cf = CouchField(val, field.field_name)
            self.fields.append(cf)
            self.groups[group].append(cf)



class CouchModel(BaseCouchModel):
    __metaclass__ = CouchModelMetaclass
