from __future__ import print_function
import time
from random import randrange
import re
from bs4 import BeautifulSoup as Soup
from . import Scraper, TemplateProcessor

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

SCRAPER = Scraper()

def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

##############################################################################
# Generate graph code
#
def generate_node_name(graph, non_existed=True):
    """
    Random name, Random chidlren name
    Avoid using existing name
    name = 3 random ASCII letters
    e.g: aaa
    """
    while True:
        node_name = ''.join([chr(randrange(97, 122)) for i in range(3)])
        if non_existed and get_node(graph, node_name):
            continue
        else:
            break
    return node_name

def generate_new_node(graph, name='', children_range=(0, 10), non_children=False):
    """
    Generate a new node with following properties:
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
        'cache': []
    }

def generate_graph(seed_count=1):
    """
    Generate a graph
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

def visit_link(node, scraper=None, children_url_re=None):
    """
    In practice, this is the fetching function
    Need to be Cached
    """
    if scraper is not None:
        node['url'] = urlparse(node['name'])
        try:
            response = scraper.goto(node['name'])
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
    return tuple(node.setdefault('children',[]))

def initial_values(node, node_count):
    node['cash'] = 1.0/node_count
    node['history'] = 0.0
    node.setdefault('cache', [])
    return node

def get_node(graph, name):
    """
    Get node in graph by name
    """
    for node in graph:
        if node['name'] == name:
            break
    else:
        log('New Node ' + name.encode('utf-8'))
        node = None
    return node

def update_node_cash(node, cash):
    """
    Update cash to the node
    """
    node['cash'] += cash
    #return node

def distribute_cash(graph, frontiers, node, scraper, children_url_re):
    """
    Distribute cash to children links
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
        children = visit_link(node, scraper, children_url_re)
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
    """
    Check if there is new child, not including in the main graph, add it into
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
    """
    Calculate node importance
    """
    importance = node['importance'] = (node['cash'] + node['history']) / (history + 1)
    log(node['name'] + ' importance: ' + str(importance))
    return importance

def merge_node(n1, n2):
    n1['cash'] += n2['cash']
    n1['history'] += n2['history'] # useless in frontier, we never fetch the page

def merge_graph(g1, g2):
    """
    update g1's nodes with g2's nodes
    """
    [merge_node(n1, n2) for n1 in g1 for n2 in g2 if n1['name'] == n2['name']]
    return g1


def start(name='tuoitre.vn', template='<div id="divContent"><getme/></div>',
          max_nodes=200, max_added_nodes=50,debug=True):
    """
    Crawl pages, and insert new pages into a frontier set. Dont crawl it
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
    """
    DEBUG = debug
    history = 0
    demo_graph = [
        {'name': 'a', 'content': 'honey money', 'children': ['b', 'c'],},
        {'name': 'b', 'content': 'money money', 'children': ['a',]},
        {'name': 'c', 'content': 'honey honey', 'children': ['a',]},
        {'name': 'd', 'content': 'honey honey honey', 'children': ['a', 'b']},
    ]

    scraper = Scraper()
    if name:
        if name.count('http://') or name.count('https://'):
            start_name = name
        else:
            start_name = 'http://' + name
        graph = [{'name': start_name}]
        children_url_re = re.compile(
            r'^((http|https)://.*' + name + '|(?!(http://|https://|javascript:)))')

    else:
        graph = generate_graph()
    frontiers = []
    t = 0
    log(graph)

    template_processor = TemplateProcessor(template)
    max_added_nodes # how many nodes added per crawling
    max_nodes # soft limit
    while True:
        t += 1
        #time.sleep(3)
        # save the last result BEFORE initial all nodes' values
        graph = [initial_values(node, len(graph)) for node in graph]
        log([x['name'] for x in graph])
        last_node = None
        while True:
            node = max(graph, key=lambda x: x['cash'])
            if node == last_node or node['cash'] == 0:
                break # break the loop, add more frontiers
            else:
                last_node = node

            history += distribute_cash(graph, frontiers, node,
                                       scraper,
                                       children_url_re)

            if node.has_key('raw_content') and not node.has_key('content'):
                node['content'] = template_processor.extract(node['raw_content'])
                log(node['content'])

        log('History :' + str(history))
        total_importance = sum([compute_importance(node, history) for node in graph])
        log('Total Importance: ' + str(total_importance))
        graph = sorted(graph,
                            key=lambda x: x.setdefault('importance', 0),
                            reverse=True)
        # get top frontiers node to main graph and keep on crawling
        # reserve graph for the next crawling
        frontiers = sorted(frontiers,
                            key=lambda x: x.setdefault('cash', 0),
                            reverse=True)
        graph_size = len(graph)
        if graph_size + max_added_nodes > max_nodes:
            break
        else:
            graph.extend(frontiers[0:max_added_nodes])

        #raw_input()

    log([x['name'] for x in graph])
    for x in graph:
        if x.has_key('content') and x['content']:
            log(x['content'])
    #return graph
