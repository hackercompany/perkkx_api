from django.conf.urls import url, patterns
from . import api
from httpproxy.views import HttpProxy
from . import interfaceApi
from utility import uApi

urlpatterns = patterns(
    '',
    url(r'^$', api.test, name='test'),
    url(r'^hproxy/(?P<url>.*)$', HttpProxy.as_view(base_url='http://hymnary.org/')),

    url(r'^query', interfaceApi.query, name='query'),
    url(r'^interface/login$', interfaceApi.login, name='interface.login'),
    url(r'^interface/post$', interfaceApi.formPost, name='interface.post'),
    url(r'^interface/form$', interfaceApi.get_form_data, name='interface.form'),
    url(r'^configuration/(?P<namespace>\w+)/(?P<key>.*)$', api.get_conf, name='configurations'),
)
