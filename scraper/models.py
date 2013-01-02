import re
import sys
import traceback
import json

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rq import job, get_connection

import requests
from db import get_table
from users.models import User
import _opic
import increment


class ScraperProfile(models.Model):
    name = models.CharField('Name', max_length=255, null=False, blank=False)
    url = models.CharField('URL', max_length=255, null=False, blank=False)
    template = models.TextField('Template', blank=True, default='')
    keywords_text = models.TextField('Keywords', blank=True, default='')

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)


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
    timeout = models.IntegerField(default=0)
    storage = get_table('websites')

    # calling self.get_status_display()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W')

    # callback URL
    callback_url = models.URLField('Callback URL', null=True, blank=True, default='')

    # meta
    meta_text = models.TextField(default='{}', null=True, blank=True)

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
    def meta(self):
        if not hasattr(self, '_session_meta'):
            print 'No __meta yet'
            self._session_meta = json.loads(self.meta_text)
            if not self._session_meta:
                print 'No meta'
                print self._session_meta
                self._session_meta = {}

        return self._session_meta

    @property
    def timestamp(self):
        return int(self.created_at.strftime('%s'))

    @models.permalink
    def get_absolute_url(self):
        return ('scraper.views.session', (), {'profile_id': str(self.profile.id),
                                              'session_id': str(self.id)})

    def save(self, *args, **kwargs):
        self.meta_text = json.dumps(self.meta)
        super(type(self), self).save(*args, **kwargs)

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
                    'history:g': str(node['history']),
                    'history:kopic': str(node['kopic'])}

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
                    print '()' * 60
                    print node['name']
                    print '()' * 60
                except Exception as e:
                    #print node
                    print 'ERRRRRRRRRRRRRRROOR'
                    #print node['name']
                    print node['name'], e
                    print "Exception in user code:"
                    print '-' * 60
                    traceback.print_exc(file=sys.stdout)
                    print '-' * 60
                    print 'end'

            print 'NOW SEND PATCH'
            b.send()

        else:
            success = False

        return success

    def get_node(self, node_name, columns=(), exact=False, include_timestamp=False):
        return self.storage.row(node_name, columns,
                                timestamp=int(self.created_at.strftime('%s')),
                                include_timestamp=include_timestamp)

    def all_nodes(self, columns, exact=True, include_timestamp=True):
        nodes = [node for node in self.storage.scan(
            columns=columns, timestamp=self.timestamp + 1,
            include_timestamp=include_timestamp)
            if (not exact) or int(node[1][columns[0]][1]) == self.timestamp]

        #sorting

        return nodes[:self.max_nodes]


def request_callback_url(session):
    """Righ after the scraping session finished, call the callback url"""
    return requests.post(session.callback_url) if session.callback_url else None


@receiver(post_save, sender=ScraperSession)
def queue_scraping(sender, **kwargs):
    if kwargs['created']:
        new_session = kwargs['instance']
        scrape.delay(new_session.id)

def parse_url_pattern(url):
    r = re.compile(r'(?P<head>.*){{(?P<expression>.*)}}(?P<tail>.*)')
    matches = re.match(url)
    if matches:
        expression = matches.groupdict()['expression']
        head = matches.groupdict()['head']
        tail = matches.groupdict()['tail']

        er = re.compile(r'(?P<min>\d+)(-{0,1})(?P<max>\d+)')
        em = er.match(expression)

        if em:
            min_id = em['min']
            max_id = em['max']
            if not max_id:
                max_id, min_id = min_id, 0

            return {'head': head, 'tail': tail, 'min': min_id, 'max': max_id}

    return None

@job('default', connection=get_connection('default'), timeout=60000)
def scrape(session_id):
    session = ScraperSession.objects.get(pk=session_id)
    profile = session.profile
    session.status = 'P'
    session.save()

    try:
        params = parse_url_pattern(profile.url)
        if params:
            result = increment.start(head=params['head'],
                                     tail=params['tail'],
                                     min_id=params['min'],
                                     max_id=params['max'],
                                     max_nodes=session.max_nodes,
                                     template=profile.template,
                                     writer=session.save_node,
                                     cache=session.get_node)
        else:
            result = _opic.start(domain=profile.url,
                                 template=profile.template,
                                 max_nodes=session.max_nodes,
                                 max_added_nodes=session.max_added_nodes,
                                 keywords=profile.keywords,
                                 writer=session.save_node,
                                 cache=session.get_node)

        session.status = 'C'
    except Exception as ex:
        print ex
        session.status = 'F'
        result = (0, 0)  # no fetched pages, no kw found
    finally:
        session.meta['fetched_pages'] = result[0]
        session.meta['found_keywords'] = result[1]

        session.save()
        request_callback_url(session)
