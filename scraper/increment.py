from . import Crawler, TemplateProcessor

def build_url(head, tail, step):
    return head + str(step) + tail

def initial_values(node):
    node['cash'] = 0
    node['history'] = 0.0
    node['keywords_count'] = 0
    node['importance'] = 0
    node['kopic'] = 0
    node.setdefault('cache', [])
    return node

def start(head, tail, min_id=0, max_id=0, template='', max_nodes=20, writer=None, cache=None):
    crawler = Crawler()
    tp = TemplateProcessor(template)
    nodes = []
    node_count = 0
    for step in range(min_id, max_id+1):
        # check if maximum exeededs
        if node_count >= max_nodes:
            break
        else:
            node_count += 1

        # initial node
        url = build_url(head, tail, step)

        node = initial_values({'name': url})

        # crawling
        print 'cawling ' + str(url)
        response = crawler.goto(url)
        node['raw_content'] = response

        # scraping, extraction
        content = tp.extract(response)
        print content
        node['content'] = content

        # append into the list
        nodes.append(node)

        # calculate importance


        # saving
        if writer is not None:
            writer(node)

    return len(nodes), 0
