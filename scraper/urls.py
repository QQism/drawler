from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
                       url(r'^$', 'scraper.views.home', name='home'),
                       url(r'^(?P<scraper_profile_id>\d+)',
                           'scraper.views.extract',
                           name='site_profile'),
                      )
