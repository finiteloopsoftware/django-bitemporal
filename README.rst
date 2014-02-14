=================
django-bitemporal
=================

Bitemporal data support for the Django ORM.

Any change in an object is implemented in three steps.
1) Invalidate the current row
2) Create a copy of that row with valid_end_date set
3) Create the new row

All Bitemporal objects have a ForeignKey called master to MasterObject, which
represents every state the object has been in. To relate to a Bitemporal object
you should make another ForeignKey to MasterObject.

Field Types
===========

Valid Start/End Date
    When the record is active in the real world, regardless of the time it was
    active in the system.

Transaction Start/End Date
    When the record was active in the system. Effectively audit columns.

MasterObject Model Methods
=========================

get_all():
    returns a BitemporalQuerySet containing all versions of the object

get_current():
    Short cut for get_all().current().get() - returns a single version of the object

Bitemporal Model Methods
========================

amend(as_of=now(), using=None):
    After making changes to a model, call .amend() with an optional ``as_of``
    date to save the changes as effective on the ``as_of`` date. Defaults to the
    current date and time. 
    ``using`` will be passed on to ``.save()``.

update(using=None):
    After making changes which correct previous errors, call update to save the
    change while invalidating the previous values. This is equivalent to calling:
    ``obj.amend(as_of=obj.valid_start_date)``
    ``using`` will be passed on to ``.save()``.

save_during(valid_start, valid_end=TIME_CURRENT, using=None):
    Save the object in a new row with ``valid_start_date`` and ``valid_end_date``
    set for the provided interval. Existing rows which confict with the vaild
    period will be updated to have thier end points adjusted.

delete(as_of=now(), using=None):
    Will write a new row with the valid_end_date to ``as_of``
    Returns this new row

    The object which delete is called on will be in an inconsistent state after
    the call to delete.

    ``using`` will be passed on to ``.delete()``.

eradicate():
    Call the real delete method, this is hidden since you generally do not want
    to delete rows.


Manager/QuerySet Methods
=============

active():
    returns all active rows

current():
    returns all current, active rows
    shortcut for ``.active().during(now())``

during(valid_start, valid_end=None):
    If ``valid_end`` is None, it will be treated as ``valid_start + 1ms``
    Return all rows (active or not) that were valid during the interval
    ``[valid_start, valid_end)``

active_during(txn_start, txn_end=TIME_CURRENT):
    If ``txn_end`` is None, it will be treated as ``txn_start + 1ms``
    Return all rows that were active during the interval
    ``[txn_start, txn_end)``


Definitions
===========

active row
    Any row where ``txn_end_date`` is ``TIME_CURRENT`` is active.

current row
    Any row where ``valid_start_date`` < ``now()`` and ``valid_end_date`` > ``now()``

Temporal consistency invariant
    For a given ``id`` value and ``date``, there should be a single object
    identified by its ``row_id`` for which ``date`` is in the interval
    ``[valid_start_date, valid_end_date)`` and the ``txn_end_date`` ==
    ``TIME_CURRENT``
