from django.db import models
from datetime import datetime
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.manager import Manager


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
        return self.during(datetime.now())


class BitemporalManager(Manager):

    def get_query_set(self):
        return BitemporalQuerySet(self.model, using=self._db)

    def current(self):
        return self.get_query_set().current()

    def during(self, valid_start, valid_end=None):
        return self.get_query_set().during(valid_start, valid_end)


class BitemporalModelBase(models.Model):

    objects = BitemporalManager()

    id = models.IntegerField()
    row_id = models.AutoField(primary_key=True)

    valid_start_date = models.DateTimeField(auto_now_add=True)
    valid_end_date = models.DateTimeField(blank=True, null=True)

    txn_start_date = models.DateTimeField(auto_now_add=True)
    txn_end_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
        unique_together = [
            ('id', 'valid_start_date', 'valid_end_date', 'txn_end_date'),
        ]
