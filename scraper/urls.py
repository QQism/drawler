from django.conf.urls.defaults import patterns, include, url
from .handlers import SessionResource

session_resource = SessionResource()

urlpatterns = patterns('',
                       url(r'^$', 'scraper.views.home', name='home'),
                       url(r'^new/$', 'scraper.views.new_profile', name='new_profile'),
                       url(r'^(?P<profile_id>\d+)/$',
                           'scraper.views.profile',
                           name='site_profile'),
                       url(r'^(?P<profile_id>\d+)/sessions/$',
                           'scraper.views.sessions',
                           name='sessions'),
                       url(r'^(?P<profile_id>\d+)/new/$',
                           'scraper.views.new_session',
                           name='new_session'),
                       url(r'^(?P<profile_id>\d+)/(?P<session_id>\d+)/$',
                           'scraper.views.session',
                           name='session'),
                       url(r'^(?P<profile_id>\d+)/(?P<session_id>\d+)/update',
                           'scraper.views.update',
                           name='update'),
                       url(r'api/', include('scraper.api_urls')),
                       url(r'api1/', include(session_resource.urls)),
                      )
