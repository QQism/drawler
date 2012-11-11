from django.db import models
from db import get_table
import pprint

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

    def write_log(self, *args, **kwargs):
        print

    def save_node(self, data):
        success = False
        if isinstance(data, dict):
            # this is the single node, in dictionary type
            pass
        elif hasattr(data, '__iter__'):
            # list of nodes
            nodes = data
            #pprint.PrettyPrinter(indent=4).pprint(nodes)
            with self.storage.batch(timestamp=int(self.created_at.strftime('%s')),
                                    batch_size=1000) as b:
                for node in nodes:
                    try:
                        b.put(node['name'].encode('utf-8'),
                          {'text:raw': node['raw_content'],
                           'text:content': u' '.join(node['content']),
                           'text:keywords_count': str(node['keywords_count']),
                           'history:opic': str(node['importance']),
                           'history:g': str(node['history']),
                          })
                    except Exception as e:
                        #print node
                        print node['name']
                        print e
        else:
            success = False

        return success
