# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ScraperSession.status'
        db.add_column('scraper_scrapersession', 'status',
                      self.gf('django.db.models.fields.CharField')(default='C', max_length=1),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ScraperSession.status'
        db.delete_column('scraper_scrapersession', 'status')


    models = {
        'scraper.scraperprofile': {
            'Meta': {'object_name': 'ScraperProfile'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords_text': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'scraper.scrapersession': {
            'Meta': {'object_name': 'ScraperSession'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_added_nodes': ('django.db.models.fields.IntegerField', [], {}),
            'max_nodes': ('django.db.models.fields.IntegerField', [], {}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['scraper.ScraperProfile']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'timeout': ('django.db.models.fields.IntegerField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['scraper']