from django.conf.urls import patterns, include, url
from criticalsyncing.core.views import Index
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', Index.as_view(), name='home'),
    url(r'^admin/', include(admin.site.urls)),
)
