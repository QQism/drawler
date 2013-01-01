from . import Crawler, TemplateProcessor

def build_url(head, tail, step):
    return head + str(step) + tail

def start(head, tail, min_id=0, max_id=0, template='', max_nodes=20, writer=None, cache=None):
    crawler = Crawler()
    tp = TemplateProcessor(tp)
    nodes = []
    for step in range(min_id, max_id+1):
        # initial node
        url = build_url(head, tail, step)
        node = {'name': url}
        # crawling
        response = crawler.goto(url)
        # scraping, extraction
        tp.extract(response.content)
        
        # saving
    return
