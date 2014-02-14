from django.db import models
from django.contrib.contenttypes.models import ContentType
from bitemporal.models import BitemporalModelBase, MasterObject

# Create your models here.

class Contact(BitemporalModelBase):

    name = models.CharField(max_length=512)
    is_organization = models.BooleanField(default=True)
    spouse = models.ForeignKey(
        MasterObject,
        null=True,
        blank=True,
        # Must be lamda to delay execution
        limit_choices_to=lambda: {'content_type': ContentType.objects.get_for_model(Contact)})

    def __unicode__(self):
        out = "pk={o.pk}, master={o.master}, valid_start_date="\
              "{o.valid_start_date}, valid_end_date={o.valid_end_date},"\
              "txn_end_date="\
              "{o.txn_end_date}, name={o.name}, is_organization="\
              "{o.is_organization}".format(o=self)

        return unicode(out)
