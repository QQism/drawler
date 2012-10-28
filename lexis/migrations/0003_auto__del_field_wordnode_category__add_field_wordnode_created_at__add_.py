# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'WordNode', fields ['plain']
        db.delete_unique('lexis_wordnode', ['plain'])

        # Deleting field 'WordNode.category'
        db.delete_column('lexis_wordnode', 'category_id')

        # Adding field 'WordNode.created_at'
        db.add_column('lexis_wordnode', 'created_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=None, blank=True),
                      keep_default=False)

        # Adding field 'WordNode.updated_at'
        db.add_column('lexis_wordnode', 'updated_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=None, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'WordNode.category'
        db.add_column('lexis_wordnode', 'category',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['lexis.Category']),
                      keep_default=False)

        # Deleting field 'WordNode.created_at'
        db.delete_column('lexis_wordnode', 'created_at')

        # Deleting field 'WordNode.updated_at'
        db.delete_column('lexis_wordnode', 'updated_at')

        # Adding unique constraint on 'WordNode', fields ['plain']
        db.create_unique('lexis_wordnode', ['plain'])


    models = {
        'lexis.category': {
            'Meta': {'object_name': 'Category'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'lexis.meanword': {
            'Meta': {'object_name': 'MeanWord'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lexis.Category']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'word': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lexis.Word']"})
        },
        'lexis.word': {
            'Meta': {'object_name': 'Word'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['lexis.Category']", 'through': "orm['lexis.MeanWord']", 'symmetrical': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plain': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'lexis.wordnode': {
            'Meta': {'ordering': "['tree_id', 'lft']", 'object_name': 'WordNode'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'plain': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'rgt': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'word': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lexis.MeanWord']"})
        }
    }

    complete_apps = ['lexis']