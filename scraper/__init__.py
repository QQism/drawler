import mechanize
import cookielib
import os
from StringIO import StringIO
import gzip
from bs4 import BeautifulSoup
#import pdb; pdb.set_trace()

class Crawler(object):
    cookie = None
    response = None
    base_url = ''
    COOKIEFILE = 'mycookie'
    default_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4'
    default_url = 'http://www.example.com'

    def __init__(self, base_url=default_url,
                 user_agent=default_user_agent, debug=False):

        self.br = mechanize.Browser()
        self.br.set_cookiejar(Crawler.get_cookie())
        self.br.set_handle_equiv = True
        #self.br.set_handle_redirect(True)
        self.br.set_handle_referer = True
        self.br.set_handle_robots = False

        if debug:
            self.br.set_debug_http = True
            self.br.set_debug_redirects = True
            self.br.set_debug_responses = True

        self.base_url = base_url
        self.br.addheaders = [('User-agent', user_agent)]
        self.response = self.br.open(self.base_url).read()

    def login(self):
        if self.login_form_attrs.has_key('id'):
            self.br.select_form(
                predicate=lambda form: hasattr(form, 'attrs') and
                form.attrs.get('id') == self.login_form_attrs['id'])

        elif self.login_form_attrs.has_key('name'):
            self.br.select_form(
                predicate=lambda form: hasattr(form, 'attrs') and
                form.attrs.get('name') == self.login_form_attrs['name'])
        else:
            self.br.select_form(
                predicate=lambda form: form.attrs == self.login_form_attrs)

        for key, value in self.login_info_attrs.items():
            self.br.form[key] = value

        self.br.submit()

    @classmethod
    def save_cookie(cls):
        if isinstance(cls.cookie, cookielib.LWPCookieJar):
            cls.cookie.save(cls.COOKIEFILE)

    def reload(self):
        self.response = self.process(self.br.open(self.base_url))
        Crawler.save_cookie()
        return self.response

    def goto(self, url):
        self.response = self.process(self.br.open(url))
        return self.response

    def process(self, response):
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        else:
            data = response.read()
        return data

    @classmethod
    def get_cookie(cls):
        if cls.cookie is None:
            cls.cookie = cookielib.LWPCookieJar()
        else:
            if os.path.isfile(cls.COOKIEFILE):
                cls.cookie.load(cls.COOKIEFILE)
        cls.cookie.save(cls.COOKIEFILE)
        return cls.cookie

demo_template = "<authentication>" +\
        "<form>" +\
        "<input name ='' value=''/>" +\
        "<input name ='' value=''/>" +\
        "</form>" +\
        "</authentication>" +\
        "<extraction>" +\
        "<div class='boxMnuMainTop'>" +\
        "<ul id='MainMnu'><getme/></ul></div><span><getme/></span>" +\
        "</extraction>"
demo_document = "<html><head></head><div class='boxMnuMainTop'><ul id='MainMnu'>ACK</ul></div></html>"

class TemplateProcessor(object):
    """
    create an instructions array from the template
    TODO login
    """

    def __init__(self, template):
        self.template = template

        self.template = BeautifulSoup(template)
        self.instructions = []

        for getme in self.template.find_all('getme'):
            parent_nodes = getme.find_parents()
            parent_nodes.pop() # pop out the last, which is *not* a Tag object
            #parent_nodes.pop() # pop out the last, which is *not* a Tag object
            parent_nodes.reverse()
            self.instructions.append(parent_nodes)

    def extract(self, document):
        """
        Extract content from document, followed by instructions
        """
        soup = BeautifulSoup(document)
        total_contents = []
        for instruction in self.instructions:
            #print instruction
            contents = self.call_childnode(soup, instruction, 0)
            if contents:
                total_contents.append(self.dearray(contents))

        return self.dearray(total_contents)

    def call_childnode(self, node, instruction, level):
        #print node, level
        if len(instruction) == level:
            return node.text
        else:
            instruction_node = instruction[level]
            level += 1
            contents = [self.call_childnode(childnode, instruction, level)
                        for childnode in node.find_all(instruction_node.name,
                                                       attrs=instruction_node.attrs)]

            return self.dearray(contents)

    def dearray(self, elements):
        """ return the only element, *not* array """
        if isinstance(elements, list) and len(elements) == 1:
            return self.dearray(elements[0])
        return elements
