from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns( '',
    # Examples:
    # url(r'^$', 'alfanousDjango.views.home', name='home'),
    url( r'^jos2', 'alfanous-django.wui.views.jos2' ),
    url( r'^admin/', include( admin.site.urls ) ),
    url( r'^(?P<language>\w{2})/(?P<unit>\w{3,15})/', 'alfanous-django.wui.views.results' ),
    url( r'^(?P<language>\w{2})/', 'alfanous-django.wui.views.results' ),
    url( r'^(?P<unit>\w{3,15})/(?P<language>\w{2})/', 'alfanous-django.wui.views.results' ),
    url( r'^(?P<unit>\w{3,15})/', 'alfanous-django.wui.views.results' ),
    url( r'^', 'alfanous-django.wui.views.results' ),
 )
