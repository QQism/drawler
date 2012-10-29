import time
import signal
import sys

def visit_link():
    pass

def initial_values(node):
    node.setdefault('visited', False)
    if not node['visited']:
        node['cash'] = 1/3.0
        node['history'] = 0
    return node

def exit_handler(signal, frame):
    print signal
    print frame
    print 'Canceled!'
    sys.exit(0)

def get_node_index(graph, name):
    for node in graph:
        if node['name'] == name:
            break
    else:
        print 'New Node'
    return graph.index(node)

def distribute_cash(graph, node):
    print '==========='
    print 'Browsing ', node['name'], node
    node['history'] += node['cash']
    l = len(node['children'])
    if l > 0:
        for child_name in node['children']:
            child_index = get_node_index(graph, child_name)
            child = graph[child_index]
            #TODO not really reference varaible ??XXX
            print 'child ', child
            child['cash'] += node['cash'] / l
    #history += node['cash']
    node['cash'] = 0
    node['visited'] = True
    print '==========='

def start():
    history = 0
    demo_graph = [
        {'name': 'a', 'content': 'honey money', 'children': ['b', 'c'],},
        {'name': 'b', 'content': 'money money', 'children': ['a',]},
        {'name': 'c', 'content': 'honey honey', 'children': ['a',]}
    ]
    [initial_values(node) for node in demo_graph]
    print demo_graph
    while True:
        time.sleep(3)
        [distribute_cash(demo_graph, node) for node in demo_graph]
        print demo_graph

    return demo_graph
signal.signal(signal.SIGINT, exit_handler)
