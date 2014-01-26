import copy
from datetime import datetime, timedelta

from django.db import IntegrityError
from django.db import models, transaction
from django.db.models import Q
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.utils.timezone import now as utcnow
from django.utils.timezone import utc


TIME_CURRENT = datetime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=utc)
TIME_RESOLUTION = timedelta(0, 0, 1) # = 1 microsecond


class BitemporalQuerySet(QuerySet):

    def get(self, *args, **kwargs):
        if 'pk' in kwargs:
            kwargs['id'] = kwargs['pk']
            del kwargs['pk']

        return super(BitemporalQuerySet, self).get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        if 'pk' in kwargs:
            kwargs['id'] = kwargs['pk']
            del kwargs['pk']

        return super(BitemporalQuerySet, self).filter(*args, **kwargs)

    @transaction.commit_on_success
    def delete(self):
        for obj in self:
            obj.delete()

    def during(self, valid_start, valid_end=None):
        if valid_end is None:
            # Single data searches single point in time
            valid_end = valid_start + TIME_RESOLUTION

        # Any equal times are outside the period
        # because of end point exclusion
        return self.filter(
            # obj.start before p.end OR obj.end after p.start
            Q(_valid_start_date__lt=valid_end) |
            Q(_valid_end_date__gt=valid_start),
        ).exclude(
            # BUT NOT
            # obj.end before p.start OR obj.end after p.end
            Q(_valid_end_date__lte=valid_start) |
            Q(_valid_start_date__gte=valid_end)
        )

    def active_during(self, txn_start, txn_end=None):
        if txn_end is None:
            # Single data searches single point in time
            txn_end = txn_start + TIME_RESOLUTION

        # Any equal times are outside the period
        # because of end point exclusion
        return self.filter(
            # obj.start before p.end OR obj.end after p.start
            Q(_txn_start_date__lt=txn_end) |
            Q(_txn_end_date__gt=txn_start),
        ).exclude(
            # BUT NOT
            # obj.end before p.start OR obj.end after p.end
            Q(_txn_end_date__lte=txn_start) |
            Q(_txn_start_date__gte=txn_end)
        )

    def active(self):
        return self.filter(
            # transaction active
            _txn_end_date=TIME_CURRENT,
        )

    def current(self):
        return self.active().during(utcnow())


class BitemporalManager(Manager):

    def get_query_set(self):
        return BitemporalQuerySet(self.model, using=self._db)

    def during(self, valid_start, valid_end=None):
        return self.get_query_set().during(valid_start, valid_end)

    def active_during(self, txn_start, txn_end=None):
        return self.get_query_set().active_during(tnx_start, tnx_end)

    def active(self):
        return self.get_queryset().active()

    def current(self):
        return self.get_query_set().current()


class BitemporalModelBase(models.Model):

    objects = BitemporalManager()

    id = models.IntegerField(blank=True, null=True)
    row_id = models.AutoField(primary_key=True)

    # nicht fur der gefingerpoken
    _valid_start_date = models.DateTimeField()
    _valid_end_date = models.DateTimeField(default=TIME_CURRENT)

    _txn_start_date = models.DateTimeField(auto_now_add=True)
    _txn_end_date = models.DateTimeField(default=TIME_CURRENT)

    @property
    def valid_start_date(self):
        return self._valid_start_date

    @property
    def valid_end_date(self):
        return self._valid_end_date

    @property
    def txn_start_date(self):
        return self._txn_start_date

    @property
    def txn_end_date(self):
        return self._txn_end_date

    class Meta:
        abstract = True
        unique_together = [
            ('id', '_valid_start_date', '_valid_end_date', '_txn_end_date'),
        ]
        ordering = ('_valid_start_date', )

    def _original(self):
        return self.__class__.objects.get(row_id=self.row_id)

    def save(self, as_of=None, force_insert=False, force_update=False, using=None, update_fields=None):
        """ if as_of is provided, self.valid_start_date is set to it.
        if self.valid_start_date is undefined, it is set to now.
        """
        now = utcnow()

        if as_of is not None:
            self._valid_start_date = as_of

        if self.valid_start_date is None:
            self._valid_start_date = now

        if self.txn_end_date != TIME_CURRENT and self.txn_end_date > now:
            raise IntegrityError('txn_end_date date {} may not be in the future'.format(
                self.txn_end_date))

        if self.valid_start_date > self.valid_end_date:
            raise IntegrityError('valid_start_date date {} must precede valid_end_date {}'.format(
                self.valid_start_date, self.valid_end_date))

        # _txn_start_date is None before first save
        if self.txn_start_date and self.txn_start_date > self.txn_end_date:
            raise IntegrityError('txn_start_date date {} must precede txn_end_date {}'.format(
                self.txn_start_date, self.txn_end_date))

        if self.txn_start_date is None and self.txn_end_date != TIME_CURRENT:
            raise IntegrityError('txn_end_date {} must be TIME_CURRENT for new transactions'.format(
                self.txn_end_date))

        # TODO: why save_base and not super().save()
        self.save_base(using=using, force_insert=force_insert,
                       force_update=force_update, update_fields=update_fields)

        # Double save for new objects? use something else to generate ids?
        if not self.id:
            self.id = self.row_id
            self.save_base(using=using, update_fields=('id',))

    @transaction.commit_on_success
    def save_during(self, valid_start, valid_end=None, using=None):
        now = utcnow()
        if valid_end is None:
            valid_end = TIME_CURRENT

        # Itterate rows while invalidating them
        def row_builder(rows):
            for row in rows:
                row._txn_end_date = now
                row.save(using=using, update_fields=['_txn_end_date',])
                yield row

        # All rows with data in the time period (includes self._original() if needed)
        old_rows = row_builder(self.__class__.objects.active().during(valid_start, valid_end).filter(id=self.id))
        try:
            resume_through = None

            old = old_rows.next()
            if old.valid_start_date < valid_start:
                if old.valid_end_date > valid_end:
                    # update inside single larger record
                    # save old end_date for later
                    resume_through = old.valid_end_date

                # Old value exists before update, set valid_end_date
                old.row_id = None
                old._valid_end_date = valid_start
                old._txn_start_date = now
                old._txn_end_date = TIME_CURRENT
                old.save(using=using)

                if resume_through is not None:
                    # Old value continues after update
                    old.row_id = None
                    old._valid_start_date = valid_end
                    old._valid_end_date = resume_through
                    # txn times still now/TIME_CURRENT
                    old.save(using=using)

                old = old_rows.next()

            if old.valid_start_date == valid_start:
                # Old start is exactly the same, it is being updated and will have no valid period

                if old.valid_end_date > valid_end:
                    # Old value continues after update
                    old.row_id = None
                    old._valid_start_date = valid_end
                    old._txn_start_date = now
                    old._txn_end_date = TIME_CURRENT
                    old.save(using=using)
                old = old_rows.next()

            while True:
                # old.valid_start_date is > valid_start (and < valid_end)
                if old.valid_end_date > valid_end:
                    # old value exists beyond valid_end

                    # Old value continues after update
                    old.row_id = None
                    old._valid_start_date = valid_end
                    old._txn_start_date = now
                    old._txn_end_date = TIME_CURRENT
                    old.save(using=using)

                # This will stop the while, not hit the try/except
                old = old_rows.next()

        except StopIteration:
            pass

        # Save a new row
        self.row_id = None
        self._valid_start_date = valid_start
        self._valid_end_date = valid_end
        self._txn_start_date = now
        self._txn_end_date = TIME_CURRENT
        self.save(using=using)

    @transaction.commit_on_success
    def amend(self, as_of=None, using=None):
        """
            Invalidate self
            Write old data with valid_end set
            write new data
        """
        now = utcnow()
        if as_of is None:
            as_of = now

        if self.txn_end_date != TIME_CURRENT:
            #Raise error, must change an active row
            raise IntegrityError('[{}] row_id: {} is not an active row'.format(
                self.__class__.__name__, self.row_id))

        if as_of > self.valid_end_date:
            raise IntegrityError('as_of date {} must precede valid_end_date {}'.format(
                as_of, self.valid_end_date))

        old_self = self._original()

        if old_self.valid_start_date != self.valid_start_date:
            raise IntegrityError('You may not change valid_start_date in an update or amend, use save_during')

        if self.valid_end_date != old_self.valid_end_date:
            raise IntegrityError('You may not change valid_end_date in an update or amend, use save_during')

        # Optimized for replacing a single row
        # invalidate previous row
        old_self._txn_end_date = now
        old_self.save(using=using, update_fields=['_txn_end_date',])

        # If valid_start == as_of, don't save a new row that covers no time
        # This was an update
        if old_self.valid_start_date != as_of :
            # Save new row with updated valid end date
            old_self.row_id = None
            old_self._txn_start_date = now
            old_self._txn_end_date = TIME_CURRENT
            old_self._valid_end_date = as_of

            # save change
            old_self.save(using=using)

        # Save self as new row
        self.row_id = None

        self._txn_start_date = now
        self._txn_end_date = TIME_CURRENT
        self._valid_start_date = as_of

        self.save(using=using)

    def update(self, using=None):
        """
            an amend where:
            old values were never true, valid_date range will be null
        """
        self.amend(as_of=self.valid_start_date, using=using)

    def eradicate(self, *args, **kwargs):
        return super(BitemporalModelBase, self).delete(*args, **kwargs)

    @transaction.commit_on_success
    def delete(self, as_of=None, using=None):
        """
            Invalidate self
            Write new row with valid_end_date set
        """

        now = utcnow()
        if as_of is None:
            as_of = now

        if self.valid_end_date != TIME_CURRENT:
            raise IntegrityError('Cannot delete non-current object')

        # Refetch data so we don't update any fields
        old_self = self._original()
        old_self._txn_end_date = now
        # invalidate previous row
        old_self.save(using=using, update_fields=['_txn_end_date',])

        # Save new row with valid end date
        old_self.row_id = None
        old_self._txn_start_date = now
        old_self._txn_end_date = TIME_CURRENT
        old_self._valid_end_date = as_of

        # save change
        old_self.save(using=using)
        return old_self

class BitemporalRelations(object):
    pass
