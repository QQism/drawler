from django.conf.urls.defaults import patterns, include, url

from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from handlers import ScraperSessionHandler

auth = HttpBasicAuthentication()
ad = {} # {'authentication': auth}

session_resource = Resource(ScraperSessionHandler, **ad)

urlpatterns = patterns('',
        url(r'^sessions/(?P<pk>\d+)/$', session_resource),
        )
