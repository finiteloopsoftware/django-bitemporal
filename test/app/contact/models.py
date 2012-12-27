from django.db import models
from bitemporal.models import BitemporalModelBase

# Create your models here.

class Contact(BitemporalModelBase):

    name = models.CharField(max_length=512)
    is_organization = models.BooleanField(default=True)

    def __unicode__(self):
        return unicode(self.name)
