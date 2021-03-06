from django.conf.urls import patterns, include, url
from django.contrib import admin
from croco.views import router

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'streaming.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
