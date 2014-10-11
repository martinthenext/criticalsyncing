# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cache'
        db.create_table('core_cache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('input_url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('output_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('core', ['Cache'])


    def backwards(self, orm):
        # Deleting model 'Cache'
        db.delete_table('core_cache')


    models = {
        'core.article': {
            'Meta': {'object_name': 'Article'},
            'authors': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Source']", 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        'core.cache': {
            'Meta': {'object_name': 'Cache'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'}),
            'output_url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'core.source': {
            'Meta': {'object_name': 'Source'},
            'bias': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'haters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'haters_rel_+'", 'blank': 'True', 'to': "orm['core.Source']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'tag': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.SourceTag']", 'symmetrical': 'False', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        'core.sourcetag': {
            'Meta': {'object_name': 'SourceTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['core']