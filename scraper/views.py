from django.shortcuts import render_to_response
from django.template import RequestContext
from models import ScraperProfile, ScraperSession
from forms import ScrapingForm
#import _opic
import logging

logger = logging.getLogger(__name__)

def home(request):
    """
    List out site profiles
    """
    profiles = ScraperProfile.objects.all()
    return render_to_response('scraper/home.html',
                              {'profiles': profiles},
                              context_instance=RequestContext(request))

def profile(request, scraper_profile_id):
    """
    Select the profile
    Choose sites to crawl
    Select template

    """
    logger.info(request)
    profile = ScraperProfile.objects.get(pk=scraper_profile_id)
    form = ScrapingForm()
    return render_to_response('scraper/profile.html',
                              {'profile': profile,
                               'form': form},
                              context_instance=RequestContext(request))

def scrape(request, scraper_profile_id):
    """
    """
    logger.info(request)
    if request.method == 'POST':
        form = ScrapingForm(request.POST)
        print(form.is_valid())
        print(form)
        if form.is_valid():
            profile = ScraperProfile.objects.get(pk=scraper_profile_id)
            new_session = ScraperSession(profile=profile,
                                         max_nodes=form.max_pages,
                                         max_added_nodes=form.page_increment,
                                         timeout=form.timeout)
            new_session.save()
            #_opic.start()
    return render_to_response('scraper/profile.html',
                              {'profile': profile,
                               'form': form},
                              context_instance=RequestContext(request))

def update(request, scraper_profile_id):
    """
    HTTP polling
    """
    return
