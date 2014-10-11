# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SourceTag'
        db.create_table('core_sourcetag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('core', ['SourceTag'])

        # Adding model 'Source'
        db.create_table('core_source', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('bias', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('core', ['Source'])

        # Adding M2M table for field tag on 'Source'
        m2m_table_name = db.shorten_name('core_source_tag')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('source', models.ForeignKey(orm['core.source'], null=False)),
            ('sourcetag', models.ForeignKey(orm['core.sourcetag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['source_id', 'sourcetag_id'])

        # Adding M2M table for field haters on 'Source'
        m2m_table_name = db.shorten_name('core_source_haters')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_source', models.ForeignKey(orm['core.source'], null=False)),
            ('to_source', models.ForeignKey(orm['core.source'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_source_id', 'to_source_id'])

        # Adding model 'Article'
        db.create_table('core_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('summary', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('authors', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Source'], blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Article'])


    def backwards(self, orm):
        # Deleting model 'SourceTag'
        db.delete_table('core_sourcetag')

        # Deleting model 'Source'
        db.delete_table('core_source')

        # Removing M2M table for field tag on 'Source'
        db.delete_table(db.shorten_name('core_source_tag'))

        # Removing M2M table for field haters on 'Source'
        db.delete_table(db.shorten_name('core_source_haters'))

        # Deleting model 'Article'
        db.delete_table('core_article')


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
        'core.source': {
            'Meta': {'object_name': 'Source'},
            'bias': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'haters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'haters_rel_+'", 'to': "orm['core.Source']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'tag': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.SourceTag']", 'symmetrical': 'False'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        'core.sourcetag': {
            'Meta': {'object_name': 'SourceTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['core']