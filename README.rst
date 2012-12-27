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

Start/End Date
    When the record is active in the real world, regardless of the time it was
    active in the system.

Transaction Start/End Date
    When the record was active in the system. Effectively audit columns.
