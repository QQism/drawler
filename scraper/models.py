from django.db import models
from db import get_table
import pprint
import sys, traceback

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

STATUS_CHOICES = (
    ('C', 'Completed'),
    ('W', 'Waiting'),
    ('P', 'Processing'),
    ('F', 'Failed')
)

class ScraperSession(models.Model):

    profile = models.ForeignKey('ScraperProfile')
    description = models.TextField()
    max_nodes = models.IntegerField()
    max_added_nodes = models.IntegerField()
    timeout = models.IntegerField()
    storage = get_table('websites')

    # calling self.get_status_display()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def finished(self):
        """Check whether the session had been finished or not
        """
        return True if self.status in ['C', 'F'] else False

    def write_log(self, *args, **kwargs):
        print


    @property
    def timestamp(self):
        return int(self.created_at.strftime('%s'))

    @models.permalink
    def get_absolute_url(self):
        return ('scraper.views.session', (), {'profile_id': str(self.profile.id),
                                              'session_id': str(self.id)})

    def save_node(self, data):
        success = False

        def pack_node(node):
            #if hasattr(node['content'], 'encode'):
            #    content = node['content'].encode('utf-8')
            #else:
            content = (u' '.join(node['content']))
            #if content:
            #    print content.encode('utf-8')
            if isinstance(node['raw_content'], unicode):
                raw_content = node['raw_content'].encode('utf-8')
            else:
                raw_content = node['raw_content']

            return {'text:raw': raw_content,
                    'text:content': content.encode('utf-8'),
                    'text:keywords_count': str(node['keywords_count']),
                    'history:opic': str(node['importance']),
                    'history:g': str(node['history'])}

        if isinstance(data, dict):
            # this is the single node, in dictionary type
            node = data
            self.storage.put(
                node['name'].encode('utf-8'),
                pack_node(node),
                timestamp=int(self.created_at.strftime('%s')))
        elif hasattr(data, '__iter__'):
            # list of nodes
            nodes = data
            #pprint.PrettyPrinter(indent=4).pprint(nodes)
            """
            with self.storage.batch(timestamp=self.timestamp,
                                    batch_size=1000) as b:
                for node in nodes:
                    try:
                        b.put(node['name'].encode('utf-8'), pack_node(node))
                        print '()'*60
                        print node['name']
                        print '()'*60
                    except Exception as e:
                        #print node
                        print 'ERRRRRRRRRRRRRRROOR'
                        #print node['name']
                        print node['name'], e
                        print "Exception in user code:"
                        print '-'*60
                        traceback.print_exc(file=sys.stdout)
                        print '-'*60
                        print 'end'
            """
            b = self.storage.batch(timestamp=self.timestamp)
            for node in nodes:
                try:
                    b.put(node['name'].encode('utf-8'), pack_node(node))
                    print '()'*60
                    print node['name']
                    print '()'*60
                except Exception as e:
                    #print node
                    print 'ERRRRRRRRRRRRRRROOR'
                    #print node['name']
                    print node['name'], e
                    print "Exception in user code:"
                    print '-'*60
                    traceback.print_exc(file=sys.stdout)
                    print '-'*60
                    print 'end'

            print 'NOW SEND PATCH'
            b.send()

        else:
            success = False

        return success

    def get_node(self, node_name, columns=(), exact=False, include_timestamp=False):
        return self.storage.row(node_name, columns,
                                timestamp=int(self.created_at.strftime('%s')))

    def all_nodes(self, columns, exact=True, include_timestamp=True):
        nodes = [node for node in self.storage.scan(
            columns=columns, timestamp=self.timestamp+1,
            include_timestamp=include_timestamp)
            if (not exact) or int(node[1][columns[0]][1]) == self.timestamp]

        #sorting

        return nodes[:self.max_nodes]
