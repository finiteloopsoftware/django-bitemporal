from datetime import datetime
import time

from django.db import IntegrityError
from django.test import TestCase
from django.utils import unittest
from django.utils.timezone import now as utcnow
from django.utils.timezone import utc

from contact import models
from bitemporal.models import TIME_CURRENT, TIME_RESOLUTION


JOHN_START = datetime(1980, 1, 1, 0, 0 ,0, tzinfo=utc)

ACME_START = datetime(1980, 10, 6, 0, 0 ,0, tzinfo=utc)
ACME_CHANGE = datetime(1997, 5, 13, 0, 0, 0, tzinfo=utc)

JANE_START = datetime(1973, 2, 22, 0, 0, 0, tzinfo=utc)
JANE_CHANGE = datetime(2003, 7, 8, 0, 0, 0, tzinfo=utc)
JANE_END = datetime(2005, 9, 18, 0, 0, 0, tzinfo=utc)

SUE_START = datetime(1971, 3, 16, 0, 0, 0, tzinfo=utc)
SUE_END = datetime(2008, 5, 21, 0, 0, 0, tzinfo=utc)

class TestContact(TestCase):

    def setUp(self):
        # John Doe Exists from JOHN_START
        obj = models.Contact(id=1,
                name=u"John Doe",
                is_organization=False,
                _valid_start_date=JOHN_START,
                _valid_end_date=TIME_CURRENT,
                _txn_start_date=utcnow(),
                _txn_end_date=TIME_CURRENT)
        obj.save()

        # Acme Corp Exists from ACME_START
        # Changes name to Acme LLC at ACME_CHANGE

        # Original Created
        obj = models.Contact(id=2,
                name=u"Acme Corp",
                is_organization=True,
                _valid_start_date=ACME_START,
                _valid_end_date=TIME_CURRENT,
                _txn_start_date=utcnow(),
                _txn_end_date=TIME_CURRENT)
        obj.save()

        now = utcnow()
        # Original invalidated
        obj._txn_end_date=now
        obj.save()

        # Original value with valid_end_date
        obj = models.Contact(id=2,
                name=u"Acme Corp",
                is_organization=True,
                _valid_start_date=ACME_START,
                _valid_end_date=ACME_CHANGE,
                _txn_start_date=now,
                _txn_end_date=TIME_CURRENT)
        obj.save()

        # New value
        obj = models.Contact(id=2,
                name=u"Acme LLC",
                is_organization=True,
                _valid_start_date=ACME_CHANGE,
                _valid_end_date=TIME_CURRENT,
                _txn_start_date=now,
                _txn_end_date=TIME_CURRENT)
        obj.save()

        # Jane Duck exists from JANE_START
        # Marries John Doe at JANE_CHANGE
        #    Name change
        #    _spouse_id set (TODO: handle reverse
        # Dies at JANE_END

        # Original created
        obj = models.Contact(id=3,
                name=u"Jane Duck",
                is_organization=False,
                _valid_start_date=JANE_START,
                _valid_end_date=TIME_CURRENT,
                _txn_start_date=utcnow(),
                _txn_end_date=TIME_CURRENT)
        obj.save()

        # Pre Change Update
        now = utcnow()
        # Orignal invalidated
        obj._txn_end_date=now
        obj.save()

        # Original with valid_end
        obj = models.Contact(id=3,
                name=u"Jane Duck",
                is_organization=False,
                _valid_start_date=JANE_START,
                _valid_end_date=JANE_CHANGE,
                _txn_start_date=now,
                _txn_end_date=TIME_CURRENT)
        obj.save()

        # New value
        obj = models.Contact(id=3,
                name=u"Jane Doe",
                is_organization=False,
                _spouse_id=1,
                _valid_start_date=JANE_CHANGE,
                _valid_end_date=TIME_CURRENT,
                _txn_start_date=now,
                _txn_end_date=TIME_CURRENT)
        obj.save()

        # Pre Delete Update
        now = utcnow()
        # New Value invalidated
        obj._txn_end_date=now
        obj.save()

        # New value with valid_end
        obj = models.Contact(id=3,
                name=u"Jane Doe",
                is_organization=False,
                _spouse_id=1,
                _valid_start_date=JANE_CHANGE,
                _valid_end_date=JANE_END,
                _txn_start_date=now,
                _txn_end_date=TIME_CURRENT)
        obj.save()

        # Sue born: SUE_START, Dies SUE_END
        # Sue's birth recorded at JANE_START
        obj = models.Contact(id=4,
                name=u"Sue Smith",
                is_organization=False,
                _valid_start_date=SUE_START,
                _valid_end_date=TIME_CURRENT,
                _txn_start_date=JANE_START,
                _txn_end_date=TIME_CURRENT)
        obj.save()

        # Pre Change Update
        now = utcnow()
        # Original invalidated
        obj._txn_end_date=now
        obj.save()

        # Set valid_end to SUE_END
        obj = models.Contact(id=4,
                name=u"Sue Smith",
                is_organization=False,
                _valid_start_date=SUE_START,
                _valid_end_date=SUE_END,
                _txn_start_date=now,
                _txn_end_date=TIME_CURRENT)
        obj.save()


    def tearDown(self):
        objs = models.Contact.objects.all()
        print
        for obj in objs:
            print unicode(obj)
            obj.eradicate()

    def test_get_current_john_doe(self):
        obj = models.Contact.objects.current().get(pk=1)
        self.assertEqual(obj.name, u"John Doe")

    def test_get_current_achme(self):
        obj = models.Contact.objects.current().get(pk=2)
        self.assertEqual(obj.name, u"Acme LLC")

    def test_get_current_jane_doe(self):
        self.assertRaises(models.Contact.DoesNotExist,
                models.Contact.objects.current().get, pk=3)

    def test_during_jane_doe_one(self):
        # between JANE_START and JANE_CHANGE
        obj = models.Contact.objects.active().during(
            datetime(1977, 1, 1, 0, 0, 0, tzinfo=utc)).get(pk=3)
        self.assertEqual(obj.name, u"Jane Duck")

    def test_during_jane_doe_two(self):
        # Range between JANE_CHANGE and JANE_END
        obj = models.Contact.objects.active().during(
            datetime(2004, 1, 1, 0, 0, 0, tzinfo=utc),
            datetime(2005, 1, 1, 0, 0, 0, tzinfo=utc)
            ).get(pk=3)
        self.assertEqual(obj.name, u"Jane Doe")

    def test_during_jane_doe_three(self):
        # Range around JANE_CHANGE
        qs = models.Contact.objects.active().during(
            datetime(2001, 1, 1, 0, 0, 0, tzinfo=utc),
            datetime(2005, 1, 1, 0, 0, 0, tzinfo=utc)
        )
        with self.assertRaises(models.Contact.MultipleObjectsReturned):
            obj = qs.get(pk=3)

        objs = qs.filter(pk=3)

        self.assertEqual(objs.count(), 2)
        self.assertEqual(objs[0].name, 'Jane Duck')
        self.assertEqual(objs[1].name, 'Jane Doe')
        # Test spouse relation
        self.assertEqual(objs[1].spouse[0].name, 'John Doe')

    def test_insert_billy_bob(self):
        obj = models.Contact(name=u"Billy Bob", is_organization=False)
        obj.save_during(utcnow(), TIME_CURRENT)

        obj = models.Contact.objects.current().get(row_id=obj.row_id)
        self.assertEqual(obj.id, obj.row_id)

    def test_update_acme(self):
        new_name = u"Acme and Sons LLC"
        obj = models.Contact.objects.current().get(pk=2)
        row_id = obj.row_id
        old_name = obj.name
        obj.name = new_name
        obj.update()  # Save a fact, replacing old value at old time
        old = models.Contact.objects.get(row_id=row_id)

        self.assertEqual(old_name, old.name)

        # Get the new object
        obj = models.Contact.objects.current().get(pk=2)
        self.assertGreater(obj.row_id, row_id)
        self.assertEqual(obj.name, new_name)

    def test_invalid_amend(self):
        # Fetch a non-current row
        new_name = u"Acme and Sons LLC"
        obj = models.Contact.objects.filter(name="Acme Corp", _txn_end_date__lt=TIME_CURRENT)[0]

        with self.assertRaises(IntegrityError):
            obj.name = new_name
            obj.amend()

    def test_invalid_update(self):
        # Fetch a non-current row
        new_name = u"Acme and Sons LLC"
        obj = models.Contact.objects.filter(name="Acme Corp", _txn_end_date__lt=TIME_CURRENT)[0]

        with self.assertRaises(IntegrityError):
            obj.name = new_name
            obj.update()

    def test_cannot_delete_jane_doe(self):
        # fetch a Non-current row
        obj = models.Contact.objects.active().during(
            datetime(1977, 1, 1, 0, 0, 0, tzinfo=utc),
        ).get(pk=3)

        with self.assertRaises(IntegrityError):
            obj.delete()

    def test_delete_john_doe(self):
        obj = models.Contact.objects.current().get(pk=1)
        then = utcnow()
        time.sleep(.1)
        obj = obj.delete()

        with self.assertRaises(models.Contact.DoesNotExist):
            obj = models.Contact.objects.current().get(pk=1)

        self.assertGreater(obj.txn_start_date, then)
        self.assertGreater(obj.valid_end_date, then)

    def test_bad_valid_period(self):
        obj = models.Contact.objects.current().get(pk=1)
        obj._valid_end_date = utcnow()
        time.sleep(.1)
        obj._valid_start_date = utcnow()

        with self.assertRaises(IntegrityError):
            obj.save()

    def test_bad_txn_period(self):
        obj = models.Contact.objects.current().get(pk=1)
        obj._txn_end_date = utcnow()
        time.sleep(.1)
        obj._txn_start_date = utcnow()

        with self.assertRaises(IntegrityError):
            obj.save()

    # Open New interval
    # new:          [
    # old in:   [   )
    # old out:  [   )
    def test_new_open_interval_1(self):
        obj = models.Contact.objects.active().during(SUE_START).get(pk=4)
        old_in = obj._original() # Fetch second copy
        # back from the dead
        obj.name = "Zombie Sue"
        obj.save_during(SUE_END)

        old_in = old_in._original() # re-Fetch row
        old_out = models.Contact.objects.active().during(SUE_START).get(pk=4)

        self.assertNotEqual(old_in.row_id, obj.row_id)
        self.assertEqual(old_in.row_id, old_out.row_id)
        # old row didn't change, still valid
        self.assertEqual(old_out.txn_end_date, TIME_CURRENT)

    # new:          [
    # old in:   [        )
    # old out:  [   )
    def test_new_open_interval_2(self):
        self.assertLess(JANE_END, SUE_END)
        obj = models.Contact.objects.active().during(SUE_START).get(pk=4)
        old_in = obj._original() # Fetch clean copy
        # back from the dead.... before she die. Original DOD was wrong?
        obj.name = "Zombie Sue"
        obj.save_during(JANE_END)

        old_in = old_in._original() # re-Fetch row
        old_out = models.Contact.objects.active().during(SUE_START).get(pk=4)

        # Total of 3 rows
        self.assertNotEqual(old_in.row_id, obj.row_id)
        self.assertNotEqual(old_in.row_id, old_out.row_id)
        # old_in is invalidated
        self.assertNotEqual(old_in.txn_end_date, TIME_CURRENT)

        # Old out is right period and valid
        self.assertEqual(old_out.valid_start_date, old_in.valid_start_date)
        self.assertEqual(old_out.valid_end_date, JANE_END)
        self.assertEqual(old_out.txn_end_date, TIME_CURRENT)

    # new:          [
    # old in:           [    )
    # old out:   Invalidated
    def test_new_open_interval_3(self):
        obj = models.Contact.objects.active().during(SUE_START).get(pk=4)
        old_in = obj._original() # Fetch clean copy
        # Corrected DOB, earlier, and not dead yet
        obj.name = "Lucky Sue"
        obj.save_during(SUE_START - (10 * TIME_RESOLUTION))

        old_in = old_in._original() # re-Fetch row
        old_missing_p = models.Contact.objects.active().filter(pk=4)

        #Only one active row
        self.assertEqual(old_missing_p.count(), 1)

        #It is obj
        self.assertEqual(old_missing_p[0].row_id, obj.row_id)

        # Total of 2 rows
        self.assertNotEqual(old_in.row_id, obj.row_id)
        # old_in is invalidated
        self.assertNotEqual(old_in.txn_end_date, TIME_CURRENT)

    # new:          [
    # old in:   [
    # old out:  [   )
    def test_new_open_interval_4(self):
        self.assertGreater(JANE_CHANGE, JOHN_START)
        obj = models.Contact.objects.active().during(JOHN_START).get(pk=1)
        old_in = obj._original() # Fetch second copy
        obj.name = "John Smith"
        obj._spouse_id = 4
        obj.save_during(JANE_CHANGE)

        old_in = old_in._original() # re-Fetch row
        old_out = models.Contact.objects.active().during(JOHN_START).get(pk=1)

        # Total of 3 rows
        self.assertNotEqual(old_in.row_id, obj.row_id)
        self.assertNotEqual(old_in.row_id, old_out.row_id)
        # old_in is invalidated
        self.assertNotEqual(old_in.txn_end_date, TIME_CURRENT)

        # Old out is right period and valid
        self.assertEqual(old_out.valid_start_date, old_in.valid_start_date)
        self.assertEqual(old_out.valid_end_date, JANE_CHANGE)
        self.assertEqual(old_out.txn_end_date, TIME_CURRENT)

    # new:          [
    # old in:       [
    # old out:   Invalidated
    def test_new_open_interval_5(self):
        obj = models.Contact.objects.active().during(JOHN_START).get(pk=1)
        old_in = obj._original() # Fetch second copy
        obj.name = "John Smith"
        obj._spouse_id = 4
        obj.save_during(JOHN_START)

        old_in = old_in._original() # re-Fetch row
        old_missing_p = models.Contact.objects.active().filter(pk=1)

        # Only one active row
        self.assertEqual(old_missing_p.count(), 1)

        # It is obj
        self.assertEqual(old_missing_p[0].row_id, obj.row_id)

        # Total of 2 rows
        self.assertNotEqual(old_in.row_id, obj.row_id)

        # old_in is invalidated
        self.assertNotEqual(old_in.txn_end_date, TIME_CURRENT)

    # new:          [
    # old in:    [  1 )[   2
    # old out:   [ 1) 2: Invalidated
    def test_new_open_interval_6(self):
        # Use list to force execution, or lazy execution happens after save.
        objs = list(models.Contact.objects.active().during(ACME_START, TIME_CURRENT).filter(pk=2))
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0].valid_end_date, objs[1].valid_start_date)
        new_obj = objs[0]._original() # Fetch second copy
        new_obj.name = "Acme Limited"
        # Correction, formed later and never changed names
        new_obj.save_during(ACME_START + (300*TIME_RESOLUTION))

        post_objs = models.Contact.objects.active().during(ACME_START, TIME_CURRENT).filter(pk=2)

        # Only two active
        self.assertEqual(post_objs.count(), 2)
        # First is a new row
        self.assertNotIn(post_objs[0].row_id, [o.row_id for o in objs])
        # Second is the updated value
        self.assertEqual(post_objs[1].row_id, new_obj.row_id)

        # First has the right dates
        old_in_1 = objs[0]
        old_out_1 = post_objs[0]
        self.assertEqual(old_out_1.valid_start_date, old_in_1.valid_start_date)
        self.assertEqual(old_out_1.valid_end_date, new_obj.valid_start_date)
        self.assertEqual(old_out_1.txn_end_date, TIME_CURRENT)


    # Closed new interval ##########
    # new:          [   2   )
    # old in:   [
    # old out:  [ 1 )       [  3
    def test_new_closed_interval_1(self):
        self.assertLess(JOHN_START, JANE_CHANGE)
        self.assertLess(JANE_END, TIME_CURRENT)

        obj = models.Contact.objects.active().during(JOHN_START).get(pk=1)
        old_in = obj._original() # Fetch second copy
        # Traded names 'till death did them part
        obj.name = 'John Duck'
        obj.save_during(JANE_CHANGE, JANE_END)

        old_in = old_in._original() # re-Fetch row
        end_rows = models.Contact.objects.active().filter(pk=1)

        # obj, is #2 of three active rows
        self.assertEqual(end_rows.count(), 3)
        self.assertEqual(end_rows[1].row_id, obj.row_id)

        # check out 1 bounds
        self.assertEqual(end_rows[0].valid_start_date, old_in.valid_start_date)
        self.assertEqual(end_rows[0].valid_end_date, obj.valid_start_date)
        self.assertEqual(end_rows[0].name, 'John Doe')

        # out 2 (New values)
        self.assertEqual(end_rows[1].valid_end_date, end_rows[2].valid_start_date)
        self.assertEqual(end_rows[1].name, 'John Duck')

        # out 3, resume original values
        self.assertEqual(end_rows[2].name, 'John Doe')
        self.assertEqual(end_rows[2].valid_end_date, TIME_CURRENT)

    # new:          [       )
    # old in:    [             )
    # old out:   [1 )       [ 2)

    # new:          [       )
    # old in:   [       )
    # old out:  [   )

    # new:          [       )
    # old in:       [       )
    # old out:   Invalidated

    # new:          [       )
    # old in:       [     )
    # old out:   Invalidated

    # new:          [       )
    # old in:         [   )
    # old out:   Invalidated

    # new:          [       )
    # old in:         [
    # old out:              [

    # new:          [       )
    # old in:         [        )
    # old out:              [  )

    # new:          [       )
    # old in:   [   1  )[   2    )
    # old out:  [ 1 )       [ 2  )
