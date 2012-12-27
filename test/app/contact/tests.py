"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from contact import models
import datetime


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


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

    def test_get_john_doe(self):
        obj = models.Contact.objects.get(pk=1)
        self.assertEqual(obj.name, u"John Doe")

    def test_get_achme(self):
        obj = models.Contact.objects.get(pk=2)
        self.assertEqual(obj.name, u"Acme LLC")
