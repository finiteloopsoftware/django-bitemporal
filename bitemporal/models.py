from django.db import models
from datetime import datetime
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.manager import Manager


class BitemporalQuerySet(QuerySet):

    def current(self):
        now = datetime.now()
        return self.filter(
            Q(valid_end_date__gte=now) | Q(valid_end_date=None),
            valid_start_date__lte=now, txn_end_date=None)


class BitemporalManager(Manager):

    def get_query_set(self):
        return BitemporalQuerySet(self.model, using=self._db)

    def current(self):
        return self.get_query_set().current()


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
