from django.conf.urls import patterns, url
from apps.main import views
from django.conf import settings
from django.conf.urls.static import static
from settings.common import MEDIA_ROOT

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),


	url(r'^expertprofile/$', views.expertprofile, name='expertprofile'),
	url(r'^expert/(?P<expertid>.+)/$', views.expert, name='expert'),


	url(r'^talks/$', views.talks, name='talks'),
	url(r'^requests/$', views.talkrequests, name='talkrequests'),
	url(r'^expertfind/$', views.expertfind, name='expertfind'),
	url(r'^tos/$', views.tos, name='tos'),
	url(r'^privacypolicy/$', views.privacypolicy, name='privacypolicy'),
	url(r'^faq/$', views.faq, name='faq'),


	(r'^media/(?P<path>.*)$', 'django.views.static.serve',
		{'document_root': MEDIA_ROOT}),
)

