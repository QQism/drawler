from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
                       url(r'^$', 'lexis.views.home', name="home"),
                       url(r'^search$', 'lexis.views.search', name="search"),
                       url(r'^words/(?P<mean_word_id>\w+)/$', 'lexis.views.get_phrases', name="get_phrases"),
                       url(r'^categories/(?P<cat_code>[\w\[\]]+)/$', 'lexis.views.get_phrases_by_category', name="get_phrases"),
                      )
