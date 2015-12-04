from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns( '',
  url( r'^jos2', 'wui.views.jos2' ),
  url(r'^r', 'wui.views.one_aya_page'),
  url(r'^$', 'wui.views.results'),
  # url( r'^admin/', include( admin.site.urls ) ),
)

# These URLs accept the language prefix.
urlpatterns += i18n_patterns('',
  url(r'^$', 'wui.views.results'),
  url(r'^(?P<unit>\w{3,15})/', 'wui.views.results'),
)

# 404 not found handler

handler404 = 'wui.views.custom_404'
