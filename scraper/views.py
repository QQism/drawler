from django.shortcuts import render_to_response
from django.template import RequestContext
from models import ScraperProfile
from forms import ScrapingForm
import _opic

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
    profile = ScraperProfile.objects.get(pk=scraper_profile_id)
    form = ScrapingForm()
    return render_to_response('scraper/profile.html',
                              {'profile': profile,
                               'form': form},
                              context_instance=RequestContext(request))

def scrape(request, scraper_profile_id):
    if request.method == 'POST':
        form = ScrapingForm(request.POST)
        if form.is_valid():
            pass
        _opic.start()
    return render_to_response('scraper/profile.html',
                              {'profile': profile,
                               'form': form},
                              context_instance=RequestContext(request))

def update(request, scraper_profile_id):
    """
    HTTP polling
    """
    return
