from piston.handler import BaseHandler
from piston.utils import rc, throttle
from tastypie.resources import ModelResource

from .models import ScraperSession

class SessionResource(ModelResource):
    class Meta:
        queryset = ScraperSession.objects.all()
        resource_name = 'session'
