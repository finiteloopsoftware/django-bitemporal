from datetime import datetime
import time

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase
from django.utils import unittest
from django.utils.timezone import now as utcnow
from django.utils.timezone import utc

from contact import models
from bitemporal.models import TIME_CURRENT, TIME_RESOLUTION, MasterObject


JOHN_START = datetime(1980, 1, 1, 0, 0 ,0, tzinfo=utc)

ACME_START = datetime(1980, 10, 6, 0, 0 ,0, tzinfo=utc)
ACME_CHANGE = datetime(1997, 5, 13, 0, 0, 0, tzinfo=utc)

JANE_START = datetime(1973, 2, 22, 0, 0, 0, tzinfo=utc)
JANE_CHANGE = datetime(2003, 7, 8, 0, 0, 0, tzinfo=utc)
JANE_END = datetime(2005, 9, 18, 0, 0, 0, tzinfo=utc)

SUE_START = datetime(1971, 3, 16, 0, 0, 0, tzinfo=utc)
SUE_END = datetime(2008, 5, 21, 0, 0, 0, tzinfo=utc)

JohnMaster = None
AcmeMaster = None
JaneMaster = None
SueMaster = None

class TestContact(TestCase):

    def setUp(self):
        content_type=ContentType.objects.get_for_model(models.Contact)
        global JohnMaster, AcmeMaster, JaneMaster, SueMaster

        JohnMaster = MasterObject(content_type=content_type)
        AcmeMaster = MasterObject(content_type=content_type)
        JaneMaster = MasterObject(content_type=content_type)
        SueMaster = MasterObject(content_type=content_type)

        JohnMaster.save()
        AcmeMaster.save()
        JaneMaster.save()
        SueMaster.save()

        # John Doe Exists from JOHN_START
        obj = models.Contact(_master=JohnMaster,
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
        obj = models.Contact(_master=AcmeMaster,
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
        obj.save(update_fields=('_txn_end_date',))

        # Original value with valid_end_date
        obj = models.Contact(_master=AcmeMaster,
                name=u"Acme Corp",
                is_organization=True,
                _valid_start_date=ACME_START,
                _valid_end_date=ACME_CHANGE,
                _txn_start_date=now,
                _txn_end_date=TIME_CURRENT)
        obj.save()

        # New value
        obj = models.Contact(_master=AcmeMaster,
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
        obj = models.Contact(_master=JaneMaster,
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
        obj.save(update_fields=('_txn_end_date',))

        # Original with valid_end
        obj = models.Contact(_master=JaneMaster,
                name=u"Jane Duck",
                is_organization=False,
                _valid_start_date=JANE_START,
                _valid_end_date=JANE_CHANGE,
                _txn_start_date=now,
                _txn_end_date=TIME_CURRENT)
        obj.save()

        # New value
        obj = models.Contact(_master=JaneMaster,
                name=u"Jane Doe",
                is_organization=False,
                spouse=JohnMaster,
                _valid_start_date=JANE_CHANGE,
                _valid_end_date=TIME_CURRENT,
                _txn_start_date=now,
                _txn_end_date=TIME_CURRENT)
        obj.save()

        # Pre Delete Update
        now = utcnow()
        # New Value invalidated
        obj._txn_end_date=now
        obj.save(update_fields=('_txn_end_date',))

        # New value with valid_end
        obj = models.Contact(_master=JaneMaster,
                name=u"Jane Doe",
                is_organization=False,
                spouse=JohnMaster,
                _valid_start_date=JANE_CHANGE,
                _valid_end_date=JANE_END,
                _txn_start_date=now,
                _txn_end_date=TIME_CURRENT)
        obj.save()

        # Sue born: SUE_START, Dies SUE_END
        # Sue's birth recorded at JANE_START
        obj = models.Contact(_master=SueMaster,
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
        obj.save(update_fields=('_txn_end_date',))

        # Set valid_end to SUE_END
        obj = models.Contact(_master=SueMaster,
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
        obj = models.Contact.objects.current().get(_master=JohnMaster)
        self.assertEqual(obj.name, u"John Doe")

    def test_get_current_achme(self):
        obj = models.Contact.objects.current().get(_master=AcmeMaster)
        self.assertEqual(obj.name, u"Acme LLC")

    def test_get_current_jane_doe(self):
        self.assertRaises(models.Contact.DoesNotExist,
                models.Contact.objects.current().get, _master=JaneMaster)

    def test_during_jane_doe_one(self):
        # between JANE_START and JANE_CHANGE
        obj = models.Contact.objects.active().during(
            datetime(1977, 1, 1, 0, 0, 0, tzinfo=utc)).get(_master=JaneMaster)
        self.assertEqual(obj.name, u"Jane Duck")

    def test_during_jane_doe_two(self):
        # Range between JANE_CHANGE and JANE_END
        obj = models.Contact.objects.active().during(
            datetime(2004, 1, 1, 0, 0, 0, tzinfo=utc),
            datetime(2005, 1, 1, 0, 0, 0, tzinfo=utc)
            ).get(_master=JaneMaster)
        self.assertEqual(obj.name, u"Jane Doe")

    def test_during_jane_doe_three(self):
        # Range around JANE_CHANGE
        qs = models.Contact.objects.active().during(
            datetime(2001, 1, 1, 0, 0, 0, tzinfo=utc),
            datetime(2005, 1, 1, 0, 0, 0, tzinfo=utc)
        )
        with self.assertRaises(models.Contact.MultipleObjectsReturned):
            obj = qs.get(_master=JaneMaster)

        objs = qs.filter(_master=JaneMaster)

        self.assertEqual(objs.count(), 2)
        self.assertEqual(objs[0].name, 'Jane Duck')
        self.assertEqual(objs[1].name, 'Jane Doe')
        # Test spouse relation
        self.assertEqual(objs[1].spouse.get_all()[0].name, 'John Doe')

    def test_insert_billy_bob(self):
        obj = models.Contact(name=u"Billy Bob", is_organization=False)
        obj.save_during(utcnow(), TIME_CURRENT)

        master = MasterObject.objects.get(pk=obj.master.pk)
        self.assertEqual(1, master.get_all().count())
        self.assertEqual(obj, master.get_current())

    def test_update_acme(self):
        new_name = u"Acme and Sons LLC"
        obj = models.Contact.objects.current().get(_master=AcmeMaster)
        pk = obj.pk
        old_name = obj.name
        obj.name = new_name
        obj.update()  # Save a fact, replacing old value at old time
        old = models.Contact.objects.get(pk=pk)

        self.assertEqual(old_name, old.name)

        # Get the new object
        obj = models.Contact.objects.current().get(_master=AcmeMaster)
        self.assertGreater(obj.pk, pk)
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
        ).get(_master=JaneMaster)

        with self.assertRaises(IntegrityError):
            obj.delete()

    def test_delete_john_doe(self):
        obj = models.Contact.objects.current().get(_master=JohnMaster)
        then = utcnow()
        time.sleep(.1)
        obj = obj.delete()

        with self.assertRaises(models.Contact.DoesNotExist):
            obj = models.Contact.objects.current().get(_master=JohnMaster)

        self.assertGreater(obj.txn_start_date, then)
        self.assertGreater(obj.valid_end_date, then)

    def test_bad_valid_period(self):
        obj = models.Contact.objects.current().get(_master=JohnMaster)
        obj._valid_end_date = utcnow()
        time.sleep(.1)
        obj._valid_start_date = utcnow()

        with self.assertRaises(IntegrityError):
            obj.save()

    def test_bad_txn_period(self):
        obj = models.Contact.objects.current().get(_master=JohnMaster)
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
        obj = models.Contact.objects.active().during(SUE_START).get(_master=SueMaster)
        old_in = obj._original() # Fetch second copy
        # back from the dead
        obj.name = "Zombie Sue"
        obj.save_during(SUE_END)

        old_in = old_in._original() # re-Fetch row
        old_out = models.Contact.objects.active().during(SUE_START).get(_master=SueMaster)

        self.assertNotEqual(old_in.pk, obj.pk)
        self.assertEqual(old_in.pk, old_out.pk)
        # old row didn't change, still valid
        self.assertEqual(old_out.txn_end_date, TIME_CURRENT)

    # new:          [
    # old in:   [        )
    # old out:  [   )
    def test_new_open_interval_2(self):
        self.assertLess(JANE_END, SUE_END)
        obj = models.Contact.objects.active().during(SUE_START).get(_master=SueMaster)
        old_in = obj._original() # Fetch clean copy
        # back from the dead.... before she died. Original DOD was wrong?
        obj.name = "Zombie Sue"
        obj.save_during(JANE_END)

        old_in = old_in._original() # re-Fetch row
        old_out = models.Contact.objects.active().during(SUE_START).get(_master=SueMaster)

        # Total of 3 rows
        self.assertNotEqual(old_in.pk, obj.pk)
        self.assertNotEqual(old_in.pk, old_out.pk)
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
        obj = models.Contact.objects.active().during(SUE_START).get(_master=SueMaster)
        old_in = obj._original() # Fetch clean copy
        # Corrected DOB, earlier, and not dead yet
        obj.name = "Lucky Sue"
        obj.save_during(SUE_START - (10 * TIME_RESOLUTION))

        old_in = old_in._original() # re-Fetch row
        old_missing_p = models.Contact.objects.active().filter(_master=SueMaster)

        #Only one active row
        self.assertEqual(old_missing_p.count(), 1)

        #It is obj
        self.assertEqual(old_missing_p[0].pk, obj.pk)

        # Total of 2 rows
        self.assertNotEqual(old_in.pk, obj.pk)
        # old_in is invalidated
        self.assertNotEqual(old_in.txn_end_date, TIME_CURRENT)

    # new:          [
    # old in:   [
    # old out:  [   )
    def test_new_open_interval_4(self):
        self.assertGreater(JANE_CHANGE, JOHN_START)
        obj = models.Contact.objects.active().during(JOHN_START).get(_master=JohnMaster)
        old_in = obj._original() # Fetch second copy
        obj.name = "John Smith"
        obj.spouse = SueMaster
        obj.save_during(JANE_CHANGE)

        old_in = old_in._original() # re-Fetch row
        old_out = models.Contact.objects.active().during(JOHN_START).get(_master=JohnMaster)

        # Total of 3 rows
        self.assertNotEqual(old_in.pk, obj.pk)
        self.assertNotEqual(old_in.pk, old_out.pk)
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
        obj = models.Contact.objects.active().during(JOHN_START).get(_master=JohnMaster)
        old_in = obj._original() # Fetch second copy
        obj.name = "John Smith"
        obj.spouse = SueMaster
        obj.save_during(JOHN_START)

        old_in = old_in._original() # re-Fetch row
        old_missing_p = models.Contact.objects.active().filter(_master=JohnMaster)

        # Only one active row
        self.assertEqual(old_missing_p.count(), 1)

        # It is obj
        self.assertEqual(old_missing_p[0].pk, obj.pk)

        # Total of 2 rows
        self.assertNotEqual(old_in.pk, obj.pk)

        # old_in is invalidated
        self.assertNotEqual(old_in.txn_end_date, TIME_CURRENT)

    # new:          [
    # old in:    [  1 )[   2
    # old out:   [ 1) 2: Invalidated
    def test_new_open_interval_6(self):
        # Use list to force execution, or lazy execution happens after save.
        objs = list(models.Contact.objects.active().during(ACME_START, TIME_CURRENT).filter(_master=AcmeMaster))
        self.assertEqual(len(objs), 2)
        self.assertEqual(objs[0].valid_end_date, objs[1].valid_start_date)
        new_obj = objs[0]._original() # Fetch second copy
        new_obj.name = "Acme Limited"
        # Correction, formed later and never changed names
        new_obj.save_during(ACME_START + (300*TIME_RESOLUTION))

        post_objs = models.Contact.objects.active().during(ACME_START, TIME_CURRENT).filter(_master=AcmeMaster)

        # Only two active
        self.assertEqual(post_objs.count(), 2)
        # First is a new row
        self.assertNotIn(post_objs[0].pk, [o.pk for o in objs])
        # Second is the updated value
        self.assertEqual(post_objs[1].pk, new_obj.pk)

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

        obj = models.Contact.objects.active().during(JOHN_START).get(_master=JohnMaster)
        old_in = obj._original() # Fetch second copy
        # Traded names 'till death did them part
        obj.name = 'John Duck'
        obj.save_during(JANE_CHANGE, JANE_END)

        old_in = old_in._original() # re-Fetch row
        end_rows = models.Contact.objects.active().filter(_master=JohnMaster)

        # obj, is #2 of three active rows
        self.assertEqual(end_rows.count(), 3)
        self.assertEqual(end_rows[1].pk, obj.pk)

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
