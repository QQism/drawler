from django.db import models
from treebeard import ns_tree

class Category(models.Model):
    code = models.CharField('Code', max_length=255, primary_key=True)
    name = models.TextField('Name', default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.code + ': ' + self.name

class Word(models.Model):
    plain = models.TextField('Plain', unique=True)
    categories = models.ManyToManyField(Category, through='MeanWord')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.plain

class MeanWord(models.Model):
    word = models.ForeignKey(Word)
    category = models.ForeignKey(Category)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def quick_create(cls, plain, code, code_name):
        word = Word.objects.create(plain=plain)
        cat = Category.objects.create(code=code, name=code_name)
        return MeanWord.objects.create(word=word, category=cat)

    def __unicode__(self):
        return self.word.plain + ' [' + self.category.code + ']'

class WordNode(ns_tree.NS_Node):
    word = models.ForeignKey(MeanWord)
    plain = models.TextField('Plain', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.plain = self.word.word.plain
        super(WordNode, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.plain

    def get_text(self):
        children = self.get_children()
        return self.plain + u' ' + u' '.join([child.word.word.plain\
                                              for child in children])

    class Meta:
        ordering = ['tree_id', 'lft']
