import swagger_ui
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView,TemplateView
from django.conf import settings


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from wui.views import api, one_aya_page, results, browse_aya, jos2

urlpatterns = [
                       url( r'^robots.txt$', TemplateView.as_view(
    template_name='protocols/robots.txt', content_type='text/plain')),
                       url( r'^opensearch.xml$', TemplateView.as_view(
    template_name='protocols/opensearch.xml', content_type='application/opensearchdescription+xml')),
                       url(r'^sitemap.xml$', TemplateView.as_view(
     template_name='protocols/sitemap.xml', content_type='application/xml')), #TODO generate for all ayas
                        url(r'^api/(?P<action>\w{3,15})/?', api, name='api'),
                         url(r'^jos2', jos2, name='jos2'),

                             url(r'^', include(swagger_ui.urls)),

                    url(r'^r', one_aya_page),

                       # url( r'^a/', include( admin.site.urls)),
]

# These URLs accept the language prefix.
urlpatterns += i18n_patterns(
    url(r'^surah/(?P<surah>[\w\-\ \']{2,20})/ayah/(?P<ayah>\d{1,8})', browse_aya, name='browse_aya'),

    url(r'^$', results, name='results'),
  url(r'^(?P<unit>\w{3,15})/', results, name='results_i18n'),
)

# Fall-back for non-supported languages from URL swich: xx-YY to xx to default (en)
urlpatterns += [
  url(r'^(?P<lang>[a-z]{2})-[A-Za-z]{2}/(?P<path>.*)$', RedirectView.as_view(url='/%(lang)s/%(path)s',query_string=True)),
  url(r'^[a-z]{2}/(?P<path>.*)$', RedirectView.as_view(url='/{}/%(path)s'.format(settings.LANGUAGE_CODE),query_string=True)),
]


# 404 not found handler

handler404 = 'wui.views.custom_404'
