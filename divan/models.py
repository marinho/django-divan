import re

from django.db import models


class BaseOption(models.Model):
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
