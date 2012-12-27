from django.db import models

# Create your models here.

class Contact(models.Model):

    name = models.CharField(max_length=512)
    is_organization = models.BooleanField(default=True)

    def __unicode__(self):
        return unicode(self.name)
