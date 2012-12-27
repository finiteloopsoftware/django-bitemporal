import datetime
from django.db import models


class Contact(models.Model):

    name = models.CharField(max_length=256)
    is_organization = models.BooleanField(default=False)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField(null=True, default=None)
    transaction_from = models.DateTimeField()
    transaction_to = models.DateTimeField(null=True, default=None)

    def __unicode__(self):
        return unicode(self.name)


class Address(models.Model):

    contact = models.ForeignKey(Contact)
    line_one = models.CharField(max_length=512)
    line_two = models.CharField(max_length=512, null=True, default=None)
    city = models.Charfield(max_length=512)
    state = modles.Charfield(max_length=512)
    postal_code = models.CharField(max_length=512)
    country = models.CharField(max_length=512, null=True, default=None)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField(null=True, default=None)
    transaction_from = models.DateTimeField()
    transaction_to = models.DateTimeField(null=True, default=None)

    def __unicode__(self):
        out = [self.line_one]
        if self.line_two:
            out.append(self.line_two)
        out.append("{0}, {1} {2}".format(self.city, self.state,
                                         self.postal_code))
        if self.country:
            out.append(self.country)

        return u"\n".join(out)
