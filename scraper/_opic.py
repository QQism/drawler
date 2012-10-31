from __future__ import print_function
import time
from random import randrange

DEBUG = 1
CACHE = True

def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

# Generate graph code
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

def generate_new_node(graph, name='', children_range=(0, 10)):
    """
    Generate a new node with following properties:
    - new name
    - children that links to, children nodes dont need to be another new node

    Return the new node
    """
    #if name:
    return {
        'name': name or generate_node_name(graph, non_existed=True),
        'children': [generate_node_name(graph, non_existed=False)
                     for i in range(randrange(children_range[0],
                                              children_range[1]))],
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

# end of generate graph code

def visit_link(node):
    """
    In practice, this is the fetching function
    Need to be Cached
    """
    return tuple(node['children'])

def initial_values(node, node_count):
    node['cash'] = 1.0/node_count
    node['history'] = 0.0
    return node

def get_node(graph, name):
    """
    Get node in graph by name
    """
    for node in graph:
        if node['name'] == name:
            break
    else:
        log('New Node ' + str(name))
        node = None
    return node

def update_node_cash(node, cash):
    """
    Update cash to the node
    """
    node['cash'] += cash
    #return node

def distribute_cash(graph, frontiers, node):
    """
    Distribute cash to children links
    """
    log('===========')
    log('Browsing ', node['name'], node)
    node['history'] += node['cash']

    if node['visited'] and CACHE:
        l = len(node['cache'])
        if l > 0:
            child_cash = node['cash'] / l
            [update_node_cash(child, child_cash) for child in node['cache']]
    else:
        children = visit_link(node)
        l = len(children)
        if l > 0:
            child_cash = node['cash'] / l
            for child_name in children:
                child = get_node(graph, child_name)
                if child is not None:
                    # exisiting node
                    log('child ', child)
                    update_node_cash(child, child_cash)
                else:
                    # frontier node
                    child = generate_new_node(frontiers, child_name)
                    child['cash'] = child_cash
                    frontiers.append(child)

                node['cache'].append(child)

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


def start():
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
    history = 0
    demo_graph = [
        {'name': 'a', 'content': 'honey money', 'children': ['b', 'c'],},
        {'name': 'b', 'content': 'money money', 'children': ['a',]},
        {'name': 'c', 'content': 'honey honey', 'children': ['a',]},
        {'name': 'd', 'content': 'honey honey honey', 'children': ['a', 'b']},
    ]
    graph = generate_graph()
    frontiers = []
    t = 0
    log(graph)
    max_added_nodes = 50 # how many nodes added per crawling
    max_nodes = 500 # soft limit
    while True:
        t += 1
        #time.sleep(3)
        # save the last result BEFORE initial all nodes' values
        graph = [initial_values(node, len(graph)) for node in graph]
        log(graph)
        last_node = None
        while True:
            node = max(graph, key=lambda x: x['cash'])
            if node == last_node or node['cash'] == 0:
                break # break the loop, add more frontiers
            else:
                last_node = node

            history += distribute_cash(graph, frontiers, node)

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

    return graph
