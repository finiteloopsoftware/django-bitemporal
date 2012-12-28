from django.test import TestCase
from django.utils import unittest
from contact import models
import datetime


class TestContact(TestCase):

    def setUp(self):
        obj = models.Contact(id=1,
                name=u"John Doe",
                is_organization=False,
                valid_start_date=datetime.datetime(1980, 1, 1, 0, 0 ,0),
                valid_end_date=None,
                txn_start_date=datetime.datetime.now(),
                txn_end_date=None)
        obj.save()

        obj = models.Contact(id=2,
                name=u"Acme Corp",
                is_organization=True,
                valid_start_date=datetime.datetime(1980, 10, 6, 0, 0 ,0),
                valid_end_date=None,
                txn_start_date=datetime.datetime.now(),
                txn_end_date=None)
        obj.save()

        end_date = datetime.datetime(1997, 5, 13, 0, 0, 0)
        obj.txn_end_date=end_date
        obj.save()

        obj = models.Contact(id=2,
                name=u"Acme LLC",
                is_organization=True,
                valid_start_date=end_date,
                valid_end_date=None,
                txn_start_date=datetime.datetime.now(),
                txn_end_date=None)
        obj.save()

        # First Entry
        obj = models.Contact(id=3,
                name=u"Jane Duck",
                is_organization=False,
                valid_start_date=datetime.datetime(1973, 2, 22, 0, 0, 0),
                valid_end_date=None,
                txn_start_date=datetime.datetime.now(),
                txn_end_date=None)
        obj.save()

        # Pre Change Update
        start_date = obj.valid_start_date
        new_date = datetime.datetime(2003, 7, 8, 0, 0, 0)
        obj.txn_end_date=datetime.datetime.now()
        obj.save()

        # Pre Change Set End Date
        obj = models.Contact(id=3,
                name=u"Jane Duck",
                is_organization=False,
                valid_start_date=start_date,
                valid_end_date=new_date,
                txn_start_date=datetime.datetime.now(),
                txn_end_date=None)
        obj.save()

        # Set Change
        obj = models.Contact(id=3,
                name=u"Jane Doe",
                is_organization=False,
                valid_start_date=new_date,
                valid_end_date=None,
                txn_start_date=datetime.datetime.now(),
                txn_end_date=None)
        obj.save()

        # Pre Delete Update
        start_date = obj.valid_start_date
        end_date = datetime.datetime(2005, 9, 18, 0, 0, 0)
        obj.txn_end_date=end_date
        obj.save()

        # Delete
        obj = models.Contact(id=3,
                name=u"Jane Doe",
                is_organization=False,
                valid_start_date=start_date,
                valid_end_date=end_date,
                txn_start_date=datetime.datetime.now(),
                txn_end_date=None)
        obj.save()


    def tearDown(self):
        objs = models.Contact.objects.all()
        print
        for obj in objs:
            print unicode(obj)
            obj.delete()

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
        obj = models.Contact.objects.during(
            datetime.datetime(1977, 1, 1, 0, 0, 0)).get(pk=3)
        self.assertEqual(obj.name, u"Jane Duck")

    def test_during_jane_doe_two(self):
        obj = models.Contact.objects.during(
            datetime.datetime(2004, 1, 1, 0, 0, 0),
            datetime.datetime(2005, 1, 1, 0, 0, 0)
            ).get(pk=3)
        self.assertEqual(obj.name, u"Jane Doe")

    def test_insert_billy_bob(self):
        obj = models.Contact(name=u"Billy Bob", is_organization=False)
        obj.save()

        obj = models.Contact.objects.current().get(row_id=obj.row_id)
        self.assertEqual(obj.id, obj.row_id)
