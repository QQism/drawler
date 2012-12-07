from django.conf.urls.defaults import patterns, include, url

from handlers import SessionResource, ScraperProfileResource
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(SessionResource())
v1_api.register(ScraperProfileResource())

#urlpatterns = patterns('',
#        url(r'', include(v1_api.urls)),
#        )
urlpatterns = patterns('', (r'', include(v1_api.urls)),)
