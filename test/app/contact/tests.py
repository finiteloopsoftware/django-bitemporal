"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from contact import models

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class TestContact(TestCase):

    def setUp(self):
        self.one = models.Contact(id=1, name=u"John Doe", is_organization=False)
        self.two = models.Contact(id=2, name=u"Acme Corp", is_organization=True)
        self.three = models.Contact(id=2, name=u"Acme LLC", is_organization=True)

    def test_add(self):
        self.one.save()
        self.two.save()

    def test_get_john_doe(self):
        obj = models.Contact.objects.get(pk=1)
        self.assertEqual(obj.name, u"John Doe")

    def test_get_achme(self):
        obj = models.Contact.objects.get(pk=2)
        self.assertEqual(obj.name, u"Acme LLC")

