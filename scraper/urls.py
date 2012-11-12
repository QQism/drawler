from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
                       url(r'^$', 'scraper.views.home', name='home'),
                       url(r'^(?P<profile_id>\d+)/$',
                           'scraper.views.profile',
                           name='site_profile'),
                       url(r'^(?P<profile_id>\d+)/sessions/$',
                           'scraper.views.sessions',
                           name='sessions'),
                       url(r'^(?P<profile_id>\d+)/(?P<session_id>\d+)',
                           'scraper.views.session',
                           name='session'),
                       url(r'^(?P<profile_id>\d+)/scrape/update',
                           'scraper.views.update',
                           name='update'),
                      )
