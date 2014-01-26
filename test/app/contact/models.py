from django.db import models
from bitemporal.models import BitemporalModelBase

# Create your models here.

class TemporalFK(object):
    """Assumes obj is an instance of BitemporalModelBase
        id_field is the name of a field containing an id to relate to
        type_ is the class of the related model
    """
    def __init__(self, to, id_field, ):
        self.id_field = id_field
        # TODO Convert to to class
        self.to = to

    def __get__(self, obj, type=None):
        if obj is None:
            return None

        # TODO filter on what?
        return to.objects.filter()

    def __set__(self, obj, value):
        pass

    def __delete__(self, obj):
        pass



class Contact(BitemporalModelBase):

    name = models.CharField(max_length=512)
    is_organization = models.BooleanField(default=True)
    # Temporal FK
    _spouse_id = models.IntegerField(null=True, blank=True)
    #spouse = models.ManyToManyField('self', to_field='id', symmetrical=True)

    def __unicode__(self):
        out = "row_id={o.row_id}, id={o.id}, valid_start_date="\
              "{o.valid_start_date}, valid_end_date={o.valid_end_date},"\
              "txn_end_date="\
              "{o.txn_end_date}, name={o.name}, is_organization="\
              "{o.is_organization}".format(o=self)

        return unicode(out)


    def get_spouse(self):
        """
            returns a queryset, because there may be multiple
        """
        # What dates?! -- our valid dates, duh
        return self.__class__.objects.during(
            self.valid_start_date, self.valid_end_date
        ).filter(id=self._spouse_id)

    def set_spouse(self, val):
        if isinstance(val, Contact):
            self._spouse_id = val.id
        elif isinstance(val, int):
            self._spouse_id = val
        else:
            raise TypeError('Contact object or integer required')

    spouse = property(get_spouse, set_spouse)
