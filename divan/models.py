import re

from django.conf import settings
from django.db import models
from couchdb import Server, client

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
    field_type = models.CharField(max_length=255)
    group = models.CharField(max_length=255, blank=True, default='')
    order = models.IntegerField(editable=False)
    help_text = models.TextField(blank=True)
    required = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ('group', 'order',)

    def save(self, *args, **kwargs):
        if not self.id:
            self.key = re.sub(r'(\W+)', r'_', self.field_name.lower())
            try:
                self.order = self.__class__.objects.order_by('-order')[0].order + 1
            except IndexError:
                self.order = 1
        super(BaseOption, self).save(*args, **kwargs)

    @property
    def couchdb(self):
        server_address = getattr(opts, 'server', None) or DEFAULT_COUCH_SERVER
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
        opts = new_class._meta = getattr(new_class, 'Meta', None)
        if opts is not None:
            server_address = getattr(opts, 'server', None) or DEFAULT_COUCH_SERVER
            server = Server(server_address)
            db_name = getattr(opts.schema._divan, 'database', None) or settings.DEFAULT_COUCH_DATABASE
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
    def __init__(self, document_id):
        self.doc = self.database[document_id]
        model = self._meta.schema
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
            setattr(self, field.key, CouchField(val, field.field_name))
            new_attr = getattr(self, field.key)
            self.fields.append(new_attr)
            self.groups[group].append(new_attr)


class CouchModel(BaseCouchModel):
    __metaclass__ = CouchModelMetaclass
