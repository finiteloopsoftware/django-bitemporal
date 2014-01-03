import copy
from django.db import models
#from datetime import datetime
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.manager import Manager
from django.utils.timezone import now as utcnow


class BitemporalQuerySet(QuerySet):

    def get(self, *args, **kwargs):
        if 'pk' in kwargs:
            kwargs['id'] = kwargs['pk']
            del kwargs['pk']

        return super(BitemporalQuerySet, self).get(*args, **kwargs)

    def during(self, valid_start, valid_end=None):
        if valid_end:
            condition = Q(valid_end_date__gte=valid_end)
        else:
            condition = (Q(valid_end_date__gte=valid_start) |
                    Q(valid_end_date=None))

        return self.filter(condition,
            valid_start_date__lte=valid_start, txn_end_date=None)

    def current(self):
        return self.during(utcnow())


class BitemporalManager(Manager):

    def get_query_set(self):
        return BitemporalQuerySet(self.model, using=self._db)

    def current(self):
        return self.get_query_set().current()

    def during(self, valid_start, valid_end=None):
        return self.get_query_set().during(valid_start, valid_end)


class BitemporalModelBase(models.Model):

    objects = BitemporalManager()

    id = models.IntegerField(blank=True, null=True)
    row_id = models.AutoField(primary_key=True)

    valid_start_date = models.DateTimeField()
    valid_end_date = models.DateTimeField(blank=True, null=True)

    txn_start_date = models.DateTimeField(auto_now_add=True)
    txn_end_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
        unique_together = [
            ('id', 'valid_start_date', 'valid_end_date', 'txn_end_date'),
        ]

    def _clone(self):
        new_obj = copy.deepcopy(self)
        new_obj.row_id = None
        return new_obj

    def _original(self):
        return self.__class__.objects.get(row_id=self.row_id)

    def save(self, valid_start_date=None, valid_end_date=None,
            force_insert=False, force_update=False, using=None,
            update_fields=None):

        # self.valid_start_date overrides kwarg valid_start_date ??
        if not self.valid_start_date:
            self.valid_start_date = valid_start_date or utcnow()

        self.save_base(using=using, force_insert=force_insert,
                       force_update=force_update, update_fields=None)

        # Double save for new objects? use something else to generate ids?
        if not self.id:
            self.id = self.row_id
            self.save_base(using=using, update_fields=('id',))

    def ammend(self, as_of=None):
        """
            Save self, old values were true 'till now
        """
        old = self._original()
        self.row_id = None

        now = utcnow()
        if as_of is None:
            as_of = now

        old_obj.txn_end_date = now
        self.txn_start_date = now

        old_obj.valid_end_date = as_of
        self.valid_start_date = as_of

        self.save()
        old_obj.save()

    def update(self):
        """
            Save self, old values were never true, valid_date range will be null
        """
        now = utcnow()
        old_obj = self._original()
        self.row_id = None

        # End = start - this was never true
        old_obj.valid_end_date = self.valid_start_date
        old_obj.txn_end_date = now

        self.valid_start_date = old_obj.valid_start_date

        self.save()
        old_obj.save()
