from bs4 import BeautifulSoup
import re
from scraper import Crawler
import operator
from copy import copy
from math import log
import happybase

try:
    from urllib.parse import urlparse #python 3
except ImportError:
    from urlparse import urlparse

class PageNode(object):

    __scraper = Crawler()

    def __init__(self, url, cash=0.0, history=0.0):
        self.cash = cash
        self.history = history
        self.children = []
        self.text = ''

        parsed_url = urlparse(url)

        re_pattern = re.compile('(?:http|ftp|https)://')
        if not re_pattern.match(parsed_url.geturl()):
            new_url = 'http://' + url
            parsed_url = urlparse(new_url)
            self.raw_url = url
            self.url = parsed_url
        else:
            self.url = parsed_url
            url_parts = re_pattern.split(url)
            if len(url_parts) > 1:
                self.raw_url = url_parts[1]
            else:
                self.raw_url = url

    @property
    def scraper(self):
        return type(self).__scraper

    def scrape(self):
        print 'Scrape ' + self.full_url
        return self.scraper.goto(self.full_url)

    def add_child(self, child):
        # insert new child node OR return the existing node
        if type(child) is not type(self):
            # assume child is raw url
            # check whether the chidlren has this raw url
            # this filter SHOULD return only 1 node
            nodes = filter(lambda node: node.url == child , self.children)
            if len(nodes) == 1:
                child_node = nodes[0]
            else:
                # child is not in the children list yet
                child_node = PageNode(child)
                self.children.append(child_node)
        else:
            child_node = child
            if child_node not in self.children:
                self.children.append(child_node)
        return child_node

    @property
    def full_url(self):
        return self.url.geturl()

    def __cmp__(self, other):
        result = -1
        if isinstance(other, type(self)):
            if self.url == other.url:
                result = 0
            if (self.url.scheme == other.url.scheme and
                self.url.netloc == other.url.netloc):
                if (self.url.path == '/' and other.url.path == '')\
                   or (other.url.path == '/' and self.url.path == ''):
                    result = 0
        #print str(self) + ' vs ' + str(other) + ': ' + str(result)
        return result

    def distribute_importance(self):
        children_count = len(self.children)

        if children_count > 0:
            child_cash = self.cash/children_count

            for child in self.children:
                child.cash += child_cash
        g = self.cash
        self.history += self.cash
        self.cash = 0
        return g

    def compute_importance(self, g):
        return (self.cash + self.history)/ (g+1)

    def __repr__(self):
        return 'PageNode ' + self.raw_url + ', children: ' + str(len(self.children))


def get_or_append_node(page_url, pages):
    new_page = True

    for page in pages:
        if page_url == page.full_url:
            result = page
            new_page = False
            break

    if new_page:
        result = PageNode(page_url)
        pages.append(result)
    return result

IGNORE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp',
                     'gif', 'tiff', 'img', 'ico', # images
                     'css', 'js', 'coffee', 'json', 'ttf' # assets
                     'mp4', 'mp3', 'wav', 'flac',
                     'avi', 'mov', 'flv', 'wmv', 'mkv', # media
                     'xls', 'xlsx', 'doc', 'docx',
                     'ppt', 'pptx', 'pdf', # documents
                     'swf', 'zip', 'gz', 'exe',
                     'rar', 'xap', 'dmg', 'svg'] # others

ignores_re = re.compile(r'^(http|https)://.*\.(' +
                        r'|'.join(IGNORE_EXTENSIONS) +
                        r')$', re.IGNORECASE)


full_url_re = re.compile(r'^(http|https)://.*')

def is_ignored(url):
    if ignores_re.match(url):
        return True
    return False

def initialize_hbase_connection(host='127.0.0.1', port='9090'):
    connection = None
    try:
        connection = happybase.Connection(host, port)
    except Exception as e:
        print e
    return connection

def create_hbase_table(connection, table_name):
    assert hasattr(connection, 'create_table')
    connection.create_table(table_name, {'text': {'max_versions': -1,
                                                  'compression': 'GZ'},
                                         'history': {'max_versions': -1},
                                         'options': {}
                                        })

def get_table(table_name):
    connection = initialize_hbase_connection(host='127.0.0.1', port='9090')
    assert hasattr(connection, 'tables')
    if table_name not in connection.tables():
        create_hbase_table(connection, table_name)

    table = connection.table(table_name)
    return table

def build_full_url(url_string, current_url):
    if full_url_re.match(url_string):
        full_url = url_string
    elif url_string.startswith('/'):
        full_url = u''.join([current_url.scheme, '://',
                             current_url.netloc,
                             url_string])
    else:
        full_url = u''.join([current_url.scheme, '://',
                             current_url.netloc,
                             current_url.path,
                             url_string])
    return full_url

#TODO pages does not add properly, and children as well
def run(page_name='tuoitre.vn'):
    table_name = 'websites'
    websites = get_table(table_name)
    pages = []
    start_page = PageNode('http://' + page_name)

# all pages that will be compute importance
    pages.append(start_page)

    soup = BeautifulSoup(start_page.scrape())
    start_page.text = soup.text

    children_url_re = re.compile(r'^((http|https)://.*' +
                                 page_name +
                                 '|(?!(http|https)://))')

    children_urls = [build_full_url(a_tag.get('href'),
                                    start_page.url)
                     for a_tag in soup.find_all('a',
                                                href=children_url_re
                                               )]

    # initialize 2 lists
    # traversing and all pages list
    for child_url in children_urls:
        if not is_ignored(child_url):
            child_node = get_or_append_node(child_url, pages)
            if child_node is not start_page:
                start_page.add_child(child_node)

    page_count = len(pages)
    i = 0

    while i < 1:
        # start inifitte loop
        print 'START CRAWLING'
        print 'PAGE: ' + str(len(pages))
        G = 0.0
        for page in pages:
            page.cash = 1.0 / page_count
            page.history = 0

        # pages that will be crawled
        crawling_pages = copy(pages)

        print 'CRAWLING PAGE: ' + str(len(crawling_pages))

        error_pages = []
        for page in crawling_pages:
            try:
                soup = BeautifulSoup(page.scrape())
                page.text = soup.text
                children_urls = [build_full_url(a_tag.get('href'), page.url)
                              for a_tag in soup.find_all('a',
                                                         href=children_url_re
                                                        )]


                print u'Adding children ' + page.raw_url.encode('utf-8')
                for child_url in children_urls:
                    if not is_ignored(child_url):
                        child_node = get_or_append_node(child_url, pages)
                        if child_node is not page:
                            page.add_child(child_node)
                print 'Completed adding children'
                print 'Total Pages: ' + str(len(pages))
                print 'end'

                G += page.distribute_importance()
            except Exception as e:
                #print e
                #print "Cannot parse the page " + page.raw_url
                error_pages.append(page)
                print e

        for error_page in error_pages:
            try:
                pages.remove(error_page)
            except:
                pass

        # finalize
        # iterate pages
        results = []
        with websites.batch(batch_size=1000) as b:
            for page in pages:
                try:
                    point = page.compute_importance(G)
                    results.append((page.raw_url, point, len(page.children)))
                    b.put(page.raw_url.encode('utf-8'),
                          {'text:raw': page.text.encode('utf-8'),
                           'history:opic': str(point),
                           'history:cash': str(page.cash),
                           'history:g': str(page.history),
                           'options:protocol': str(page.url.scheme),
                          })
                except Exception as e:
                    #print '!!error: '
                    print page.raw_url
                    #print point
                    print e
                    error_pages.append(page)
        sorted_results = sorted(results,
                                key=operator.itemgetter(1),
                                reverse=True)

        print 'XXXXXXXXXXXXXXXXX'
        print 'XXXX!!START!!XXXX'
        for page in sorted_results:
            print page
        print 'XXXX!!!END!!!XXXX'
        print 'XXXXXXXXXXXXXXXXX'
        i += 1
        # end loop
