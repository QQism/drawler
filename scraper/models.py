from django.db import models
from db import get_table

class ScraperProfile(models.Model):
    name = models.CharField('Name', max_length=255, null=False, blank=False)
    url = models.URLField('URL', max_length=200, null=False, blank=False)
    template = models.TextField('Template', blank=True, default='')
    keywords_text = models.TextField('Keywords', blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def keywords(self):
        return self.keywords_text.split(',')

    def save(self, *args, **kwargs):
        self.keywords_text = ','.join([keyword.strip()
                                       for keyword in
                                       self.keywords_text.split(',')])
        super(type(self), self).save(*args, **kwargs)


    def __unicode__(self):
        return self.name + ': ' + self.url + ', ' + self.keywords_text

class ScraperSession(models.Model):

    profile = models.ForeignKey('ScraperProfile')
    description = models.TextField()
    max_nodes = models.IntegerField()
    max_added_nodes = models.IntegerField()
    timeout = models.IntegerField()
    storage = get_table('websites')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save_node(self, data):
        success = False
        if isinstance(data, dict):
            # this is the single node, in dictionary type
            pass
        elif hasattr(data, '__iter__'):
            # list of nodes
            nodes = data
            with self.storage.batch(batch_size=1000) as b:
                for node in nodes:
                    try:
                        b.put(node['url'],
                          {'text:raw': node['raw_content'].encode('utf-8'),
                           'text:content': node['content'].encode('utf-8'),
                           'text:keywords_count': node['keywords_count'],
                           'history:opic': node['importance'],
                           'history:g': node['history'],
                          }, timestamp=self.created_at)
                    except Exception as e:
                        print node
                        print e
        else:
            success = False

        return success
