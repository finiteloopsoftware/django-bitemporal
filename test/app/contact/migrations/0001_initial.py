# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Contact'
        db.create_table(u'contact_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_valid_start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('_valid_end_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.max.replace(tzinfo=datetime.timezone.utc))),
            ('_txn_start_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('_txn_end_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.max.replace(tzinfo=datetime.timezone.utc))),
            ('_master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['bitemporal.MasterObject'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('is_organization', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('spouse', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bitemporal.MasterObject'], null=True, blank=True)),
        ))
        db.send_create_signal(u'contact', ['Contact'])


    def backwards(self, orm):
        # Deleting model 'Contact'
        db.delete_table(u'contact_contact')


    models = {
        u'bitemporal.masterobject': {
            'Meta': {'object_name': 'MasterObject'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'contact.contact': {
            'Meta': {'ordering': "('_valid_start_date',)", 'object_name': 'Contact'},
            '_master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['bitemporal.MasterObject']"}),
            '_txn_end_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.max.replace(tzinfo=datetime_utils.timezone.utc)'}),
            '_txn_start_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            '_valid_end_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.max.replace(tzinfo=datetime_utils.timezone.utc)'}),
            '_valid_start_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_organization': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'spouse': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bitemporal.MasterObject']", 'null': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['contact']
