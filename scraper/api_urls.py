from django.conf.urls.defaults import patterns, include, url

from handlers import SessionResource

session_resource = SessionResource()

urlpatterns = patterns('',
        url(r'', include(session_resource.urls)),
        )
