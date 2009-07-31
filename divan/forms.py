from django import forms
from django.db.models import Q
from django.conf import settings
from django.utils.datastructures import SortedDict
from django.forms.widgets import media_property
from couchdb import Server, client

DEFAULT_COUCH_SERVER = getattr(settings, 'DEFAULT_COUCH_SERVER', 'http://localhost:5984/')

def create_form_field(option):
    FieldClass = getattr(forms, option.field_type)
    return FieldClass(label=option.field_name, required=option.required)

def get_saved_fields(model, groups):
    if groups is None:
        queryset = model.objects.all()
    else:
        queryset = model.objects.filter(group__in=groups)
    fields = [
        (field.key, create_form_field(field)) 
        for field in queryset.order_by('group', 'order')
    ]
    return SortedDict(fields)

def save_document(form, document_id, fields=None):
    cleaned_data = form.cleaned_data
    db = form.database
    if document_id is not None:
        document = db[document_id]
        for k, v in cleaned_data.items():
            document[k] = v
        db[document_id] = document
    else:
        doc_id = db.create(cleaned_data)
        document = db[doc_id]
    return document

class SQLFieldsMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(SQLFieldsMetaclass,
                     cls).__new__(cls, name, bases, attrs)
        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        opts = new_class._meta = getattr(new_class, 'Meta', None)
        if opts is not None:
            model = opts.model
            groups = getattr(opts, 'groups', None) 
            base_fields = get_saved_fields(model, groups)
            new_class.base_fields = base_fields
            server_address = getattr(opts, 'server', None) or DEFAULT_COUCH_SERVER
            server = Server(server_address)
            db_name = getattr(opts, 'database', None) or settings.DEFAULT_COUCH_DATABASE
            try:
                new_class.database = server[db_name]
            except client.ResourceNotFound:
                new_class.database = server.create(db_name)
        return new_class


class BaseCouchForm(forms.BaseForm):
    def __init__(self, data=None, files=None, document=None, initial=None, *args, **kwargs):
        document_data = {}
        if document is None:
            self.document_id = None
        else:
            self.document_id = document['_id']
            for k, v in document.iteritems():
                if k not in ('_id', '_rev'):
                    document_data[k] = v
        if initial is not None:
            document_data.update(initial)
        super(BaseCouchForm, self).__init__(data, files, initial=document_data,
                                            *args, **kwargs)

    def save(self):
        return save_document(self, self.document_id, self.fields)

    def full_clean(self):
        # import pdb; pdb.set_trace()
        super(BaseCouchForm, self).full_clean()
        


class CouchForm(BaseCouchForm):
    __metaclass__ = SQLFieldsMetaclass
