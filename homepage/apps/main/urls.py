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
	url(r'^messages/$', views.messages, name='messages'),
	url(r'^requests/$', views.talkrequests, name='talkrequests'),
	url(r'^expertfind/$', views.expertfind, name='expertfind'),
	url(r'^tagsearch/(?P<tags>.+)/$', views.tagsearch, name='tagsearch'),

	url(r'^payment/$', views.payment, name='payment'),
	url(r'^charge/$', views.charge, name='charge'),
	url(r'^review/$', views.review, name='review'),
	url(r'^invoice/$', views.invoice, name='invoice'),

	# url(r'^chargedashboard/$', views.chargedashboard, name='chargedashboard'),


	# twilio views
	url(r'^process_pin/$', views.process_pin, name='process_pin'),
	url(r'^gather_pin/$', views.gather_pin, name='gather_pin'),
	url(r'^call_hook/$', views.call_hook, name='call_hook'),

	url(r'^tos/$', views.tos, name='tos'),
	url(r'^privacypolicy/$', views.privacypolicy, name='privacypolicy'),
	url(r'^faq/$', views.faq, name='faq'),


	(r'^media/(?P<path>.*)$', 'django.views.static.serve',
		{'document_root': MEDIA_ROOT}),
)

