from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView,TemplateView
from django.conf import settings


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns( '',
                        url( r'^robots.txt$', TemplateView.as_view(
    template_name='protocols/robots.txt', content_type='text/plain')),
                        url( r'^opensearch.xml$', TemplateView.as_view(
    template_name='protocols/opensearch.xml', content_type='application/opensearchdescription+xml')),
                        url(r'^sitemap.xml$', TemplateView.as_view(
     template_name='protocols/sitemap.xml', content_type='application/xml')),
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

# Fall-back for non-supported languages from URL swich: xx-YY to xx to default (en)
urlpatterns += patterns('',
  url(r'^(?P<lang>[a-z]{2})-[A-Za-z]{2}/(?P<path>.*)$', RedirectView.as_view(url='/%(lang)s/%(path)s',query_string=True)),
  url(r'^[a-z]{2}/(?P<path>.*)$', RedirectView.as_view(url='/{}/%(path)s'.format(settings.LANGUAGE_CODE),query_string=True)),
)


# 404 not found handler

handler404 = 'wui.views.custom_404'
