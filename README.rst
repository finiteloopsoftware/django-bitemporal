=================
django-bitemporal
=================

Bitemporal data support for the Django ORM

Field Types
===========
Row Key
    The primary key for the row regardless of the data in the row. Used to
    leverage sequences in the underlying database for databases that don't
    support sequences.

Primary Key
    The primary key for the data itself. This column should be unique for a set
    of data but the value may not be unique across the column in the database.

Valid Start/End Date
    When the record is active in the real world, regardless of the time it was
    active in the system.

Transaction Start/End Date
    When the record was active in the system. Effectively audit columns.


Methods
=======

amend([as_of=now()], using=None, update_fields=None):
    After making changes to a model, call .ammend() with an optional `as_of`
    date to save the changes as effective on the `as_of` date. Defaults to the
    current date and time.
    `using` and `update_fields` will be passed on to `.save()`. `update_fields`
    will have the required bitemporal fields added as needed.


update(using=None, update_fields=None):
    After making changes which correct previous errors, call update to save the
    change while invalidating the previous values. This is equivalent to calling
    `obj.ammend(as_of=obj.valid_start_date)`
    `using` and `update_fields` will be passed on to `.save()`. `update_fields`
    will have the required bitemporal fields added as needed.


Definitions
===========

active row
    For a given `id` value, there should be a single object identified by its
    `row_id` for which the `txn_end_date` is None, this is the current
    representation of the object, and thus "active".
