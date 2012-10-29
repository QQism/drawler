import time

def generate_graph(count):
    pass

def visit_link(node):
    return tuple(node['children'])

def initial_values(node, node_count):
    node.setdefault('visited', False)
    if not node['visited']:
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
        print 'New Node'
    return node

def distribute_cash(graph, node):
    """
    Distribute cash to children links
    """
    print '==========='
    print 'Browsing ', node['name'], node
    node['history'] += node['cash']
    children = visit_link(node)
    l = len(children)
    if l > 0:
        for child_name in children:
            child = get_node(graph, child_name)
            print 'child ', child
            child['cash'] += node['cash'] / l
    node['cash'] = 0
    node['visited'] = True
    print '==========='
    return node['history']

def compute_importance(node, history):
    """
    Calculate node importance
    """
    importance = node['importance'] = (node['cash'] + node['history']) / (history + 1)
    print node['name'] + ' importance: ' + str(importance)
    return importance

def start():
    history = 0
    demo_graph = [
        {'name': 'a', 'content': 'honey money', 'children': ['b', 'c'],},
        {'name': 'b', 'content': 'money money', 'children': ['a',]},
        {'name': 'c', 'content': 'honey honey', 'children': ['a',]},
        {'name': 'd', 'content': 'honey honey honey', 'children': ['a', 'b']},
    ]
    [initial_values(node, len(demo_graph)) for node in demo_graph]
    print demo_graph
    while True:
        time.sleep(3)
        print demo_graph
        history = sum([distribute_cash(demo_graph, node) for node in demo_graph])
        print 'History :' + str(history)
        total_importance = sum([compute_importance(node, history) for node in demo_graph])
        print 'Total Importance: ' + str(total_importance)
        demo_graph = sorted(demo_graph,
                            key=lambda x: x.setdefault('importance', 0),
                            reverse=True)

    return demo_graph
