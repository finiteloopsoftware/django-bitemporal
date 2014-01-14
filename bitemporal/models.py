import copy
from django.db import models
#from datetime import datetime
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.manager import Manager
from django.utils.timezone import now as utcnow
from django.db import IntegrityError


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

    def _original(self):
        return self.__class__.objects.get(row_id=self.row_id)

    def save(self, as_of=None, force_insert=False, force_update=False, using=None, update_fields=None):
        """ if as_of is provided, self.valid_start_date is set to it.
        if self.valid_start_date is undefined, it is set to now.
        """

        if as_of is not None:
            self.valid_start_date = as_of

        if self.valid_start_date is None:
            self.valid_start_date = utcnow()

        self.save_base(using=using, force_insert=force_insert,
                       force_update=force_update, update_fields=update_fields)

        # Double save for new objects? use something else to generate ids?
        if not self.id:
            self.id = self.row_id
            self.save_base(using=using, update_fields=('id',))

    def amend(self, as_of=None, using=None):
        """
            Invalidate self
            Write old data with valid_end set
            write new data
        """
        now = utcnow()
        if as_of is None:
            as_of = now

        if self.txn_end_date != None:
            #Raise error, must change an active row
            raise IntegrityError('[{}] row_id: {} is not an active row'.format(
                self.__class__.__name__, self.row_id))

        if self.valid_end_date and as_of > self.valid_end_date:
            raise IntegrityError('as_of date {} must precede valid_end_date {}'.format(
                as_of, self.valid_end_date))

        old_self = self._original()
        old_self.txn_end_date = now
        # invalidate previous row
        old_self.save(using=using, update_fields=['txn_end_date',])

        # Save new row with valid end date
        old_self.row_id = None
        old_self.txn_start_date = now
        old_self.txn_end_date = None
        old_self.valid_end_date = as_of

        # save change 
        old_self.save(using=using, )

        # Save self as new row
        self.row_id = None

        self.txn_start_date = now
        self.txn_end_date = None
        self.valid_start_date = as_of

        self.save(using=using)

    def update(self, using=None):
        """
            an amend where:
            old values were never true, valid_date range will be null
        """
        self.amend(as_of=self.valid_start_date, using=using)
