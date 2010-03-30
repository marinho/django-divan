from datetime import date, datetime, time
from django import forms
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import simplejson
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext as _
from django.forms.widgets import media_property
from divan import db
from divan.models import BaseOption

try:
    from tinymce.widgets import TinyMCE
except ImportError:
    TinyMCE = forms.Textarea


field_and_kwargs = {
    BaseOption.INPUT_SELECT: (
        forms.ModelChoiceField, {}
    ),
    BaseOption.INPUT_TINYMCE: (
        forms.CharField, {
            'widget': TinyMCE    
        }
    ),
    BaseOption.INPUT_RADIO: (
        forms.ModelChoiceField,
        {
            'widget': forms.RadioSelect
        }
    ),
    BaseOption.INPUT_SELECT_MULTIPLE: (
        forms.ModelMultipleChoiceField, {}
    ),
    BaseOption.INPUT_SELECT_MULTIPLE_CHECKBOXES: (
        forms.ModelMultipleChoiceField,
        {
            'widget': forms.CheckboxSelectMultiple
        }
    )
}

def create_form_field(option, divan):
    kwargs = {}
    field_type = option.field_type
    if option.input_method == BaseOption.INPUT_STANDARD:
        FieldClass = getattr(forms, field_type)
    else:
        FieldClass, opts = field_and_kwargs[option.input_method]
        kwargs.update(opts)
        if option.input_method != BaseOption.INPUT_TINYMCE:
            kwargs['queryset'] = getattr(option, option._divan.choice_related_name).all()
    help_text = getattr(option, 'help_text', None)
    if help_text:
        help_text = _(help_text)
    return FieldClass(label=_(option.field_name), required=option.required, 
            help_text=help_text, **kwargs)

def get_saved_fields(model, groups, divan):
    if groups is None:
        queryset = model.objects.all()
    else:
        queryset = model.objects.filter(group__in=groups)
    fields = [
        (field.key, create_form_field(field, divan)) 
        for field in queryset.order_by('group', 'order')
    ]
    return SortedDict(fields)

def save_document(form, document_id, fields=None):
    cleaned_data = form.cleaned_data
    for k, v in [(k, form.fields[k]) for k in cleaned_data.keys() if form.fields.has_key(k) and cleaned_data.get(k)]:
        cls_name = v.__class__.__name__
        divan = form._divan
        if isinstance(v, forms.ModelMultipleChoiceField):
            cleaned_data[k] = [v.value for v in cleaned_data[k]]
        elif isinstance(v, forms.ModelChoiceField): 
            cleaned_data[k] = cleaned_data[k].value
        if hasattr(divan, cls_name) and cleaned_data[k] is not None:
            val = cleaned_data[k]
            func = getattr(divan, cls_name)['serialize']
            if isinstance(val, list): 
                cleaned_data[k] = [func(v) for v in val]
            else:
                cleaned_data[k] = func(val)
    if document_id is not None:
        document = db.update(document_id, cleaned_data)
    else:
        document = db.create(cleaned_data)
    return document

class SQLFieldsMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(SQLFieldsMetaclass,
                     cls).__new__(cls, name, bases, attrs)
        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        opts = getattr(new_class, 'Divan', None)
        if opts is not None:
            new_class._divan = opts() 
            model = opts.model
            groups = getattr(opts, 'groups', None) 
            base_fields = get_saved_fields(model, groups, opts)
            new_class.base_fields = base_fields
            new_class.database = db
            for field_type, serializers in db.default_serializers.items():
                if not hasattr(new_class._divan, field_type):
                    setattr(new_class._divan, field_type, serializers)
        return new_class


class BaseDivanForm(forms.BaseForm):
    def __init__(self, data=None, files=None, document=None, initial=None, *args, **kwargs):
        document_data = {}
        if document is None:
            self.document_id = None
        else:
            self.document_id = db.get_id_for_document(document)
            for k, v in document.iteritems():
                if k not in db.exclude_keys:
                    document_data[k] = v
        if initial is not None:
            document_data.update(initial)
        super(BaseDivanForm, self).__init__(data, files, initial=document_data,
                                            *args, **kwargs)
        for k, v in self.fields.items():
            if self.initial.has_key(k):
                if isinstance(v, forms.ModelMultipleChoiceField):
                    instance = self._divan.model.objects.get(key=k)
                    value_list = document_data[k]
                    self.initial[k] = [choice.id for choice in getattr(instance, instance._divan.choice_related_name).filter(value__in=value_list)]
                elif isinstance(v, forms.ModelChoiceField):
                    instance = self._divan.model.objects.get(key=k)
                    value = document_data[k]
                    self.initial[k] = getattr(instance, instance._divan.choice_related_name).get(value=value).id
                else:
                    serial = getattr(self._divan, v.__class__.__name__, None)
                    if serial is not None:
                        self.initial[k] = serial['deserialize'](self.initial[k])

    def save(self):
        return save_document(self, self.document_id, self.fields)


class DivanForm(BaseDivanForm):
    __metaclass__ = SQLFieldsMetaclass
