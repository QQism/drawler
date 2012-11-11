from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic.simple import direct_to_template
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tiengviet.views.home', name='home'),
    # url(r'^tiengviet/', include('tiengviet.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/django_rq/', include('django_rq.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^lexis/', include('lexis.urls', namespace="lexis"), name="lexis_urls"),
    url(r'^scraper/', include('scraper.urls', namespace="scraper"), name="scraper_urls"),
)
