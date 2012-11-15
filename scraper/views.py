from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from models import ScraperProfile, ScraperSession
from forms import ScrapingForm
import _opic
import logging
from django_rq import job, enqueue, get_connection

logger = logging.getLogger(__name__)

def home(request):
    """
    List out site profiles
    """
    profiles = ScraperProfile.objects.all()
    return render_to_response('scraper/home.html',
                              {'profiles': profiles},
                              context_instance=RequestContext(request))

def profile(request, profile_id):
    """
    Select the profile
    Choose sites to crawl
    Select template

    """
    logger.info(request)
    profile = ScraperProfile.objects.get(pk=profile_id)
    form = ScrapingForm()
    return render_to_response('scraper/profile.html',
                              {'profile': profile,
                               'form': form},
                              context_instance=RequestContext(request))

def sessions(request, profile_id):
    """
    """
    profile = ScraperProfile.objects.get(pk=profile_id)
    form = ScrapingForm()
    logger.info(request)
    if request.method == 'POST':
        print(request.POST)
        form = ScrapingForm(request.POST)
        print(form.is_valid())
        print(form)
        print(type(form))
        if form.is_valid():
            new_session = ScraperSession(profile=profile,
                                         max_nodes=int(form.data['max_pages']),
                                         max_added_nodes=int(form.data['pages_increment']),
                                         timeout=int(form.data['timeout']))
            new_session.save()
            #enqueue(scrape, session_id=new_session.pk)
            scrape.delay(new_session.id)
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
    nodes = [i for i in session.storage.scan(
        columns = ['history:opic', 'text:keywords_count'],
        timestamp=int(session.created_at.strftime('%s'))+1)]
    return render_to_response('scraper/session.html',
                              {'profile': profile,
                               'session': session, 'nodes': nodes},
                              context_instance=RequestContext(request))


def update(request, scraper_profile_id):
    """
    HTTP polling
    """
    return

@job('default', connection=get_connection('default'), timeout=60000)
def scrape(session_id):
    session = ScraperSession.objects.get(pk=session_id)
    profile = session.profile
    session.status = 'P'
    session.save()
    _opic.start(domain=profile.url,
                template=profile.template,
                max_nodes=session.max_nodes,
                max_added_nodes=session.max_added_nodes,
                keywords=profile.keywords,
                writer=session.save_node)
    session.status = 'C'
    session.save()

