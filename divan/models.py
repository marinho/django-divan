import re
from datetime import date, datetime, time

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from divan import db
from divan.timestamps import from_timestamp, to_timestamp


class OptionModelBase(models.base.ModelBase):
    def __init__(cls, name, bases, attrs):
        opts = getattr(cls, 'Divan', None)
        setattr(cls, '_divan', opts)


class BaseOption(models.Model):
    __metaclass__ = OptionModelBase

    INPUT_STANDARD = 0
    INPUT_SELECT = 1
    INPUT_RADIO = 2
    INPUT_SELECT_MULTIPLE = 3
    INPUT_SELECT_MULTIPLE_CHECKBOXES = 4
    INPUT_TINYMCE = 5

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
    INPUT_SELECTION_CHOICES = (
        (INPUT_STANDARD , 'Standard single input'),
        (INPUT_TINYMCE, 'WYSIWYG editor'),
        (INPUT_SELECT, 'Select box'),
        (INPUT_RADIO, 'Radio buttons'), 
        (INPUT_SELECT_MULTIPLE, 'Multiple select box'), 
        (INPUT_SELECT_MULTIPLE_CHECKBOXES, 'Multiple checkboxes'),
    )
    key = models.CharField(max_length=255, editable=False)
    field_name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=255, choices=FIELD_TYPE_OPTIONS)
    group = models.CharField(max_length=255, blank=True, default='')
    order = models.IntegerField(editable=False)
    help_text = models.TextField(blank=True)
    required = models.BooleanField(default=False)
    input_method = models.IntegerField(choices=INPUT_SELECTION_CHOICES, default=INPUT_STANDARD)

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
    def db(self):
        return db


class OptionChoice(models.Model):
    value = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.value


class DivanModelMetaclass(type):
    def __new__(cls, name, bases, dict):
        new_class = super(DivanModelMetaclass, cls).__new__(cls, name, bases, dict)
        opts = getattr(new_class, 'Divan', None)
        if opts is not None:
            new_class._divan = opts() 
            groups = getattr(opts, 'groups', None) 
            if groups is None:
                schema = new_class._divan.schema
                exclude = getattr(opts, 'exclude', None)
                if exclude is None:
                    new_class._divan.groups = list(set([
                        option.group 
                        for option in schema.objects.all()
                    ]))
                else:
                    new_class._divan.groups = list(set([
                        option.group 
                        for option in schema.objects.exclude(group__in=exclude)
                    ]))
            else:
                new_class._divan.groups = groups
            for field_type, serializers in db.default_serializers.items():
                if not hasattr(new_class._divan, field_type):
                    setattr(new_class._divan, field_type, serializers)
        return new_class


class DivanField(object):
    def __init__(self, val, label):
        self.value = val
        self.label = label

    def __unicode__(self):
        return unicode(self.value)


class BaseDivanModel(object):
    def __init__(self, document, **kwargs):
        self.doc = document
        model = self._divan.schema
        self.groups = dict((group, []) for group in self._divan.groups)
        self.fields = []
        for field in model.objects.order_by('group', 'order'):
            try:
                val = db.get_value_for_field(document, field.key)
            except AttributeError:
                continue
            cls_name = field.field_type 
            divan = self._divan
            if isinstance(val, list) and hasattr(divan, 'format_list'):
                format_list = getattr(self, getattr(divan, 'format_list'))
                if hasattr(divan, cls_name) and val:
                    func = getattr(divan, cls_name)['deserialize']
                    val = [func(v) for v in val]
                val = format_list(val)
            elif hasattr(divan, cls_name) and val:
                func = getattr(divan, cls_name)['deserialize']
                val = func(val)
            setattr(self, field.key, val)
            cf = DivanField(val, field.field_name)
            self.fields.append(cf)
            group = field.group
            if self.groups.has_key(group):
                self.groups[group].append(cf)

    def __iter__(self):
        return iter(self.fields)


class DivanModel(BaseDivanModel):
    __metaclass__ = DivanModelMetaclass
