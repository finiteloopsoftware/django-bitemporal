from django.db import models
from bitemporal.models import BitemporalModelBase

# Create your models here.

class Contact(BitemporalModelBase):

    name = models.CharField(max_length=512)
    is_organization = models.BooleanField(default=True)

    def __unicode__(self):
        out = "row_id={o.row_id}, id={o.id}, valid_start_date="\
              "{o.valid_start_date}, valid_end_date={o.valid_end_date},"\
              "txn_end_date="\
              "{o.txn_end_date}, name={o.name}, is_organization="\
              "{o.is_organization}".format(o=self)

        return unicode(out)
