from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns( '',
    # Examples:
    # url(r'^$', 'views.home', name='home'),
    url( r'^jos2', 'wui.views.jos2' ),
    url( r'^admin/', include( admin.site.urls ) ),
    url( r'^(?P<language>\w{2})/(?P<unit>\w{3,15})/', 'wui.views.results' ),
    url( r'^(?P<language>\w{2})/', 'wui.views.results' ),
    url( r'^(?P<unit>\w{3,15})/(?P<language>\w{2})/', 'wui.views.results' ),
    url( r'^(?P<unit>\w{3,15})/', 'wui.views.results' ),
    url( r'^', 'wui.views.results' ),
 )
