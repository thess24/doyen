from django.conf.urls import patterns, url
from apps.main import views
from django.conf import settings
from django.conf.urls.static import static
from settings.common import MEDIA_ROOT
from django.views.generic import TemplateView


urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),


	url(r'^editsettings/$', views.editsettings, name='editsettings'),
	url(r'^emailtest/$', views.emailtest, name='emailtest'),
	url(r'^expertprofile/$', views.expertprofile, name='expertprofile'),
	url(r'^expert/(?P<expertid>.+)/request/$', views.requesttalk, name='requesttalk'),
	url(r'^expert/(?P<expertid>.+)/$', views.expert, name='expert'),


	url(r'^talks/$', views.talks, name='talks'),
	url(r'^talkpayment/(?P<talkid>.+)/$', views.talkpayment, name='talkpayment'),
	url(r'^requests/$', views.talkrequests, name='talkrequests'),
	url(r'^expertfind/$', views.expertfind, name='expertfind'),
	url(r'^expertfind/(?P<category>.+)/$', views.expertfindcategory, name='expertfindcategory'),
	url(r'^favorites/$', views.favorites, name='favorites'),
	url(r'^tagsearch/(?P<tags>.+)/$', views.tagsearch, name='tagsearch'),

	url(r'^review/(?P<talkid>.+)/$', views.review, name='review'),
	url(r'^invoice/$', views.invoice, name='invoice'),

	url(r'^chargedashboard/$', views.chargedashboard, name='chargedashboard'),
	url(r'^rateexpert/(?P<id>.+)/$', views.rateexpert, name='rateexpert'),


	# twilio views
	url(r'^process_pin/$', views.process_pin, name='process_pin'),
	url(r'^gather_pin/$', views.gather_pin, name='gather_pin'),
	url(r'^call_hook/$', views.call_hook, name='call_hook'),


	# static views -- TemplateView not used bc I wanted to route in template
	url(r'^tos/$', views.tos, name='tos'),
	url(r'^privacypolicy/$', views.privacypolicy, name='privacypolicy'),
	url(r'^faq/$', views.faq, name='faq'),
	url(r'^about/$', views.about, name='about'),


	(r'^media/(?P<path>.*)$', 'django.views.static.serve',
		{'document_root': MEDIA_ROOT}),
	# move this outside only if in debug mode
)

