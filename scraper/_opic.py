# -*- coding: utf-8 -*-
from __future__ import print_function
import time
from random import randrange
import re
from bs4 import BeautifulSoup as Soup
from . import Crawler, TemplateProcessor
import re

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

DEBUG = 1
CACHE = True

IGNORE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp',
                     'gif', 'tiff', 'img', 'ico', # images
                     'css', 'js', 'coffee', 'json', 'ttf' # assets
                     'mp4', 'mp3', 'wav', 'flac',
                     'avi', 'mov', 'flv', 'wmv', 'mkv', # media
                     'xls', 'xlsx', 'doc', 'docx',
                     'ppt', 'pptx', 'pdf', # documents
                     'swf', 'zip', 'gz', 'exe',
                     'rar', 'xap', 'dmg', 'svg'] # others

IGNORE_RE = re.compile(r'^(http|https)://.*\.(' +
                        r'|'.join(IGNORE_EXTENSIONS) +
                        r')$', re.IGNORECASE)

FULL_URL_RE = re.compile(r'^(http|https)://.*')

def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

##############################################################################
# Generate graph code
#
def generate_node_name(graph, non_existed=True):
    """Random name, Random chidlren name
    Avoid using existing name
    name = 3 random ASCII letters
    e.g: aaa
    """
    while True:
        node_name = ''.join([chr(randrange(97, 122)) for i in range(1)])
        if non_existed and get_node(graph, node_name):
            continue
        else:
            break
    return node_name

def generate_new_node(graph, name='', children_range=(0, 10), non_children=False):
    """Generate a new node with following properties:
    - new name
    - children that links to, children nodes dont need to be another new node

    Return the new node
    """
    if not name:
        name = generate_node_name(graph, non_existed=True)
    if non_children:
        children = []
    else:
        children = [generate_node_name(graph, non_existed=False)
                     for i in range(randrange(children_range[0],
                                              children_range[1]))]
    return {
        'name': name,
        'children': children,
        'visited': False,
        'history': 0.0,
        'keywords_count': 0,
        'cache': []
    }

def generate_graph(seed_count=1):
    """Generate a graph
    seed_count: number of starting nodes
    """
    graph = []
    [graph.append(generate_new_node(graph, children_range=(1, 5)))
     for i in range(seed_count)]
    return graph
#
# end of generate graph code
##############################################################################

def build_full_url(url_string, current_url):
    #log('xxxxxxxxxx')
    #log(url_string)
    #log(current_url)
    if FULL_URL_RE.match(url_string):
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
    #log(full_url)
    #log('xxxxxxx')
    return full_url

def visit_link(node, crawler=None, children_url_re=None, cache=None):
    """In practice, this is the fetching function
    Need to be Cached
    """
    if crawler is not None:
        node['url'] = urlparse(node['name'])
        try:
            response = None
            if cache:
                result = cache(node['name'], ['text:raw'])
                #log(result)
                #input()
                if result:
                    response = result['text:raw']
                    log(node['name'], 'CACHE')

            if not response:
                response = crawler.goto(node['name'])

            soup = Soup(response)
            node['raw_content'] = response

            # internal pages
            node['children'] = [build_full_url(a_tag.get('href'),
                                               node['url'])
                                for a_tag in soup.find_all('a',
                                                           href=children_url_re
                                                          )]
        except Exception as ex:
            log(node['name'], ex)
            node['children'] = []
            node['raw_content'] = u''

    return tuple(node.setdefault('children',[]))

def initial_values(node, node_count):
    node['cash'] = 1.0/node_count
    node['history'] = 0.0
    node.setdefault('cache', [])
    return node

def get_node(graph, name):
    """Get node in graph by name
    """
    for node in graph:
        if node['name'] == name:
            break
    else:
        log('New Node ' + name.encode('utf-8'))
        node = None
    return node

def update_node_cash(node, cash):
    """Update cash to the node
    """
    node['cash'] += cash
    #return node

def distribute_cash(graph, frontiers, node, crawler, children_url_re, cache):
    """Distribute cash to children links
    """
    log('===========')
    log('Browsing ', node['name'])
    node['history'] += node['cash']

    if node.setdefault('visited', False) and CACHE:
        l = len(node['cache'])
        if l > 0:
            child_cash = node['cash'] / l
            [update_node_cash(child, child_cash) for child in node['cache']]
    else:
        children = visit_link(node, crawler, children_url_re, cache=cache)
        l = len(children)
        if l > 0:
            child_cash = node['cash'] / l
            for child_name in children:
                child = get_node(graph, child_name)
                if child is not None:
                    # exisiting node
                    #log('child ', child)
                    update_node_cash(child, child_cash)
                else:
                    # frontier node
                    child = generate_new_node(frontiers, child_name, non_children=True)
                    child['cash'] = child_cash
                    frontiers.append(child)

                node.setdefault('cache', []).append(child)

    node['cash'] = 0
    node['visited'] = True
    log('===========')
    return node['history']

def classify_children(graph, children):
    """Check if there is new child, not including in the main graph, add it into
    frontier set
    """
    existing_nodes = []
    frontier_nodes = []
    for child in children:
        node = get_node(graph, child)
        if not node:
            existing_nodes.append(node)
        else:
            frontier_nodes.append(node)
    return (existing_nodes, frontier_nodes)

def compute_importance(node, history):
    """Calculate node importance
    """
    importance = node['importance'] = (node['cash'] + node['history']) / (history + 1)
    log(node['name'] + ' importance: ' + str(importance))
    return importance

def merge_node(n1, n2):
    n1['cash'] += n2['cash']
    n1['history'] += n2['history'] # useless in frontier, we never fetch the page

def merge_graph(g1, g2):
    """update g1's nodes with g2's nodes
    """
    [merge_node(n1, n2) for n1 in g1 for n2 in g2 if n1['name'] == n2['name']]
    return g1

def build_keywords_re(keywords):
    kw = ur'|'.join(keywords)
    return re.compile(ur'(' + kw + ')', re.UNICODE + re.IGNORECASE)

def keywords_occurances(node, keywords_re):
    try:
        content = node.setdefault('content', ())
        node['keywords_count'] = sum([len(keywords_re.findall(i))
                                          for i in content])
    except Exception as ex:
        log(ex)
        log(node['name'])
        log(node.setdefault('content', ()))
        node['keywords_count'] = 0

    return node['keywords_count']

def start(domain='tuoitre.vn', template='<div id="divContent"><getme/></div>',
          max_nodes=10, max_added_nodes=2, keywords=(u'trung quốc',),
          session=None, writer=None, fake=False, cache=True, debug=True):
    """Crawl pages, and insert new pages into a frontier set. Dont crawl it
    immediately, wait for the next time

    Dont select all pages in frontier set, choose best/most popular pages
    By that way, we can handle how fast crawling progress

    For reducing bandwidth, we may consider not crawling a page (to parse
    the children) more than 2nd times, but still existing children (cache) to
    distribute cash

    Crawling till all cash on pages go to zero
    Advantages: easy to handle how far the crawler goes
    Disadvantages: Freshness

    Fetching Policy:
    Set an interval for all pages to be re-fetched
    Dont fetch pages that

    :param domain: domain of the site need to be scraped
    :param template: template is used to extract the content of a page in part
    :param max_nodes: integer, maximum nodes(pages) that are allowed to be
                      fetched, default is `100`
    :param max_added_nodes: integer, maximum nodes(pages) that are allowed to be fetched
                            per iteration, default is `50`
    :param keywords: tuple of keywords that are used to filter the result
    :param fake: boolean value, in case of `True` don't fetch any page,
                 try to generate fake data
    :param debug: logging or not
    :param writer: a function that is used to write the result into disk/DB/file
                   with param is node or nodes
    """
    DEBUG = debug
    history = 0

    crawler = Crawler()
    if domain:
        if domain.count('http://') or domain.count('https://'):
            full_url = domain
            domain = re.sub('^(http|https)://','', domain)
        else:
            full_url = 'http://' + domain
        graph = [{'name': full_url}]
        children_url_re = re.compile(
            r'^((http|https)://.*' + domain + '|(?!(http://|https://|javascript:)))')

    else:
        children_url_re = None
        graph = generate_graph()
    frontiers = []
    t = 0
    log(graph)

    template_processor = TemplateProcessor(template)
    max_added_nodes # how many nodes added per crawling
    max_nodes # soft limit
    kw_re = build_keywords_re(keywords)
    total_occurances = 0
    while True:
        t += 1
        #time.sleep(3)
        # save the last result BEFORE initial all nodes' values
        graph = [initial_values(node, len(graph)) for node in graph]
        log([x['name'] for x in graph])
        last_node = None
        while True:
            """" the select node that has most cash """
            node = max(graph, key=lambda x: x['cash'])
            if node == last_node or node['cash'] == 0:
                """
                All cash has been distributed
                """
                break # break the loop, add more frontiers
            else:
                last_node = node

            history += distribute_cash(graph, frontiers, node,
                                       crawler,
                                       children_url_re, cache)

            if node.has_key('raw_content') and not node.has_key('content'):
                log('SSSSSSSSS')
                log(node['name'])
                content = template_processor.extract(node['raw_content'])
                if hasattr(content, 'encode'):
                    # content should be in tuple, not str or unicode
                    content = (content, )
                node['content'] = content
                log(content)
                log('ssssssssssss')

        log('History :' + str(history))
        total_importance = total_occurances = 0
        for node in graph:
            total_importance += compute_importance(node, history)
            total_occurances += keywords_occurances(node, kw_re)

        #total_importance = sum([compute_importance(node, history) for node in graph])
        log('Total Importance: ' + str(total_importance))
        graph = sorted(graph,
                            key=lambda x: x.setdefault('importance', 0),
                            reverse=True)


        if writer is not None:
            log('Start insert into DB')
            writer(graph)
            log('Successfully')

        # get top frontiers node to main graph and keep on crawling
        # reserve graph for the next crawling
        frontiers = sorted(frontiers,
                            key=lambda x: x.setdefault('cash', 0),
                            reverse=True)
        graph_size = len(graph)
        available_added_nodes = max_nodes - graph_size



        if available_added_nodes == 0:
            """
            we hit the upper bound
            Try to calculate the keyword points
            """
            #total_occurances += sum([keywords_occurances(node, kw_re) for node in graph])
            break
        elif max_added_nodes > available_added_nodes:
            graph.extend(frontiers[0:available_added_nodes])
        else:
            graph.extend(frontiers[0:max_added_nodes])

        #raw_input()

    graph = sorted(graph,
                   key=lambda x: x.setdefault('importance', 0),
                   reverse=True)

    log('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    [log(x['name'], x['importance']) for x in graph]


    if writer is not None:
        log('Start insert into DB')
        writer(graph)
        log('Successfully')

    for x in graph:
        if x.has_key('content') and x['content'] and x['keywords_count'] > 0:
#            log(x['content'])
            log(x['keywords_count'])
    return total_occurances
    #return graph
