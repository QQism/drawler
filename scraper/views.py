from django.shortcuts import render_to_response
from django.template import RequestContext
from models import ScraperProfile
from scraper import Scraper, TemplateProcessor

def home(request):
    """
    List out site profiles
    """
    scraper_profiles = ScraperProfile.objects.all()
    print scraper_profiles
    return render_to_response('scraper/home.html',
                              {'profiles': scraper_profiles},
                              context_instance=RequestContext(request))

def extract(request, scraper_profile_id):
    """
    Select the profile
    Choose sites to crawl
    Select template

    """
    pass
