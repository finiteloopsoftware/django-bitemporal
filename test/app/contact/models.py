from django.db import models
from django.contrib.contenttypes.models import ContentType
from bitemporal.models import BitemporalModelBase, MasterObject

# Create your models here.

class Contact(BitemporalModelBase):

    name = models.CharField(max_length=512)
    is_organization = models.BooleanField(default=True)
    _spouse = models.ForeignKey(
        MasterObject,
        null=True,
        blank=True,
        related_name='spouse_set',
        db_column='spouse_id',
        limit_choices_to={'content_type': ContentType.objects.get_by_natural_key('contact', 'contact')}
    )

    def __unicode__(self):
        out = "pk={o.pk}, master={o.master}, valid_start_date="\
              "{o.valid_start_date}, valid_end_date={o.valid_end_date},"\
              "txn_end_date="\
              "{o.txn_end_date}, name={o.name}, is_organization="\
              "{o.is_organization}".format(o=self)

        return unicode(out)

    @property
    def spouse_qs(self):
        # I have one
        if self._spouse:
            # Bitemporal QS of current spouse
            return self._spouse.get_all()
        # One points to me
        return self.master.spouse_set.during(self._valid_start_date, self._valid_end_date)
