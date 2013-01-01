from functools import wraps
import json
import logging

from django.core import serializers
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django_rq import job, enqueue, get_connection

import requests

from models import ScraperProfile, ScraperSession
from forms import ScraperSessionForm, ScraperProfileForm
import _opic

logger = logging.getLogger(__name__)

from .xmldict import array_to_xml

def http_basic_auth(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        from django.contrib.auth import authenticate, login
        if request.META.has_key('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if authmeth.lower() == 'basic':
                auth = auth.strip().decode('base64')
                username, password = auth.split(':', 1)
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
        return func(request, *args, **kwargs)
    return _decorator

@http_basic_auth
@login_required
def home(request):
    """List out site profiles
    """
    profiles = request.user.scraperprofile_set.all()
    #profiles = ScraperProfile.objects.all()
    return render_to_response('scraper/home.html',
                              {'profiles': profiles},
                              context_instance=RequestContext(request))

@http_basic_auth
@login_required
def new_profile(request):
    if request.method == 'GET':
        form = ScraperProfileForm()
    elif request.method == 'POST':
        form = ScraperProfileForm(request.POST)
        if form.is_valid():
            data = form.data
            profile = ScraperProfile(name=data['name'],
                    url=data['url'],
                    template=form['template'].value(),
                    keywords_text=form['keywords'].value(),
                    user=request.user)
            profile.save()
            return redirect('scraper:home')
        else:
            pass
    return render_to_response('scraper/new_profile.html',
            {'form': form},
            context_instance=RequestContext(request))

@http_basic_auth
@login_required
def profile(request, profile_id):
    """Select the profile
    Choose sites to crawl
    Select template
    """
    logger.info(request)
    profile = ScraperProfile.objects.get(pk=profile_id)
    form = ScraperSessionForm()
    sessions = ScraperSession.objects.filter(profile=profile).order_by('-created_at')
    return render_to_response('scraper/profile.html',
                              {
                                  'profile': profile,
                                  'form': form,
                                  'sessions': sessions
                              },
                              context_instance=RequestContext(request))

@csrf_exempt
@http_basic_auth
#@login_required
def sessions(request, profile_id):
    """
    """
    profile = ScraperProfile.objects.get(pk=profile_id)
    form = ScraperSessionForm()
    logger.info(request)
    print request
    if request.method == 'POST':
        if request.META['HTTP_ACCEPT'] == 'application/json':
            items = request.POST.items()
            post = json.loads(items[0][0])

            max_nodes = int(post['max_pages'])
            max_added_nodes = max_nodes/4
            max_added_nodes = 1 if max_added_nodes == 0 else max_added_nodes

            new_session = ScraperSession(profile=profile,
                                         max_nodes=max_nodes,
                                         max_added_nodes=max_added_nodes,
                                         callback_url=post['callback_url'],
                                         timeout=int(post['timeout']))
            new_session.save()
            data = {'message': 'Success'}

            return HttpResponse(json.dumps(data), mimetype='application/json')
        else:
            form = ScraperSessionForm(request.POST)
            if form.is_valid():
                max_nodes = int(post['max_pages'])
                max_added_nodes = max_nodes/4
                max_added_nodes = 1 if max_added_nodes == 0 else max_added_nodes

                new_session = ScraperSession(profile=profile,
                                             max_nodes=max_nodes,
                                             max_added_nodes=max_added_nodes,
                                             timeout=int(form.data['timeout']))
                new_session.save()
                #enqueue(scrape, session_id=new_session.pk)
                #scrape.delay(new_session.id)
                #_opic.start()
                return redirect('scraper:session', profile_id=profile.id,
                                session_id=new_session.id)
            else:
                return render_to_response('scraper/profile.html',
                                          {'profile': profile,
                                           'form': form},
                                          context_instance=RequestContext(request))

def session(request, profile_id, session_id):
    session = ScraperSession.objects.get(pk=session_id)
    profile = session.profile
    sessions = ScraperSession.objects.filter(profile=profile).order_by('-created_at')
    columns = ['history:opic', 'text:keywords_count' ,'text:content', 'history:kopic']

    nodes = session.all_nodes(columns)
    nodes = extract_nodes(nodes)

    return render_to_response('scraper/profile.html',
                              {'profile': profile, 'sessions': sessions,
                               'current_session': session, 'nodes': nodes},
                              context_instance=RequestContext(request))


def new_session(request, profile_id):
    profile = ScraperProfile.objects.get(pk=profile_id)
    form = ScraperSessionForm()
    sessions = ScraperSession.objects.filter(profile=profile).order_by('-created_at')
    return render_to_response('scraper/profile.html',
                              {
                                  'profile': profile,
                                  'form': form,
                                  'sessions': sessions
                              },
                              context_instance=RequestContext(request))

def update(request, profile_id, session_id):
    """
    HTTP polling
    """
    session = ScraperSession.objects.get(pk=session_id)
    response = {'polling': True}
    if session.finished:
        response['polling'] = False

    columns = ['history:opic', 'text:keywords_count' ,'text:content', 'history:kopic']
    nodes = session.all_nodes(columns)

    response['nodes'] = sorted([(node[0], node[1]['history:opic'][0],
                                 node[1]['text:keywords_count'][0],
                                 node[1]['text:content'][0])
                                for node in nodes],
                               key=lambda node: float(node[1][0]),
                               reverse=True)

    return HttpResponse(json.dumps(response), mimetype='application/json')


def extract_nodes(nodes, limit=100):
    return sorted([(node[0], node[1]['history:opic'][0],
                    node[1]['text:keywords_count'][0],
                    node[1]['text:content'][0],
                    node[1]['history:kopic'][0])
                   for node in nodes],
                  key=lambda node: float(node[4]),
                  reverse=True)[:limit]


def result(request, profile_id, session_id, format):
    session = ScraperSession.objects.get(pk=session_id)
    columns = ['text:content',]
    nodes = session.all_nodes(columns, include_timestamp=True)
    mimetype = 'application/' + format
    if format == 'xml':
        _nodes = [wrap_node(node, for_xml=True) for node in nodes]
        result = pack_nodes(_nodes)
    elif format == 'json':
        _nodes = [wrap_node(node) for node in nodes]
        result = json.dumps(_nodes, ensure_ascii=False)
    return HttpResponse(result, mimetype=mimetype)

def total_sessions(request):
    pass

def pack_nodes(nodes):
    return array_to_xml(nodes, 'node')

def wrap_node(node, for_xml=False):
    _node = {'url': node[0]}

    _ex = {}
    for key,value in node[1].iteritems():
        # keys: 'text:content', need 'content'
        kparts = key.split(':')
        kparts.reverse()
        _key = kparts[0]
        if for_xml:
            text = '<![CDATA[' + value[0] + ']]>'
        else:
            text = value[0]
        _ex[_key] = {'value': text, 'timestamp': value[1]}

    _node.update(_ex)
    return _node

def request_callback_url(session):
    """Righ after the scraping session finished, call the callback url"""
    return requests.post(session.callback_url) if session.callback_url else None
