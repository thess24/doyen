from django.shortcuts import render, get_object_or_404
from apps.main.models import ExpertProfile, Talk, Rating, Message, Favorite
from apps.main.models import TalkForm, ExpertProfileForm, RatingForm, MessageForm, TalkReplyForm
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from settings.common import MEDIA_ROOT
from django.db.models import Sum
import stripe
import requests
from django.http import HttpResponse, HttpResponseRedirect, Http404
from twilio import twiml
from django_twilio.decorators import twilio_view
import datetime  # arrow? 


def index(request):
	context= {}
	return render(request, 'main/index.html', context)

def tagsearch(request,tags):
	taglist = tags.split("+")
	experts = ExpertProfile.objects.filter(tags__name__in=taglist).distinct()
	print taglist
	# for e in experts:
	# 	print e.tags.all()
	context = {'experts':experts}
	return render(request, 'main/expertfind.html', context)	

def expert(request, expertid):
	# currenttime = datetime.datetime.now()

	expert = get_object_or_404(ExpertProfile, id=expertid)
	reviews = Rating.objects.filter(expert_id=expertid)
	favorites = Favorite.objects.filter(user=request.user)
	# finished_talks = Talk.objects.filter(user=request.user,accepted=True,time__gt=currenttime)


	messageform = MessageForm()
	requestform = TalkForm()
	ratingform = RatingForm()


	if request.method=='POST':
	# make ajax form here, also make sure user signed up
		if 'requestform' in request.POST:
			form = TalkForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.expert = expert.user
				instance.user = request.user
				instance.save()

				return HttpResponseRedirect(reverse('apps.main.views.talks', args=()))

		if 'sendmessage' in request.POST:
			form = MessageForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.reciever = expert.user
				instance.sender = request.user
				instance.save()

				return HttpResponseRedirect(reverse('apps.main.views.talks', args=()))

		if 'ratingform' in request.POST:
			form = RatingForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.expert = expert.user
				instance.user=request.user
				instance.save()

				return HttpResponseRedirect(reverse('apps.main.views.talks', args=()))


	context = {'expert':expert,'favorites':favorites, 'reviews':reviews, 'requestform':requestform, 'messageform':messageform, 'ratingform':ratingform}
	return render(request, 'main/expert.html',context)

def expertprofile(request):
	try: expert = ExpertProfile.objects.get(user=request.user)
	except: expert = None

	form = ExpertProfileForm(instance=expert)

	if request.method=='POST':
		if 'updateprofile' in request.POST:
			form = ExpertProfileForm(request.POST, request.FILES, instance=expert)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.user=request.user
				instance.save()
				form.save_m2m()


				return HttpResponseRedirect(reverse('apps.main.views.expertprofile', args=()))

	context= {'expert':expert, 'form':form}
	return render(request, 'main/expertprofile.html', context)	

@login_required
def messages(request):
	inbox = Message.objects.filter(reciever = request.user)
	outbox = Message.objects.filter(sender = request.user)

	newmessages = inbox.filter(read_at=None).count()

	form = MessageForm()

	# if request.method=='POST':
	# 	if 'sendmessage' in request.POST:
	# 		form = ExpertProfileForm(request.POST)
	# 		if form.is_valid():
	# 			instance = form.save(commit=False)
	# 			instance.user=request.user
	# 			instance.save()

	# 			return HttpResponseRedirect(reverse('apps.main.views.messages', args=()))	


	context = {'inbox':inbox,'outbox':outbox, 'form':form, 'newmessages':newmessages}
	return render(request, 'main/messages.html', context)	

def expertfind(request):
	experts = ExpertProfile.objects.filter(online=True)

	if request.user.is_authenticated:
		favorites = Favorite.objects.filter(user=request.user)
	else:
		favorites = []

	context = {'experts':experts}
	return render(request, 'main/expertfind.html', context)	

@login_required
def talks(request):

	# only times for future
	# revise for fewer queries
	talks = Talk.objects.filter(user=request.user, accepted=True)
	reqtalks = Talk.objects.filter(user=request.user)


	context = {'talks':talks, 'reqtalks':reqtalks}
	return render(request, 'main/talks.html', context)	

@login_required
def talkrequests(request):
	expert = get_object_or_404(ExpertProfile, user=request.user)

	reqtalks = Talk.objects.filter(expert = request.user,requested=True)


	talkreplyform = TalkReplyForm()

	if request.method=='POST':
		reqid = request.POST.get('requestid','')
		reqinstance = reqtalks.get(id=reqid)

		if 'acceptform' in request.POST:
			form = TalkReplyForm(request.POST,instance=reqinstance)
			if form.is_valid():
				instance = form.save(commit=False)

				instance.cancelled = False
				instance.accepted = True
				instance.requested = False
				instance.price = expert.price

				instance.user=request.user
				instance.save()

				'''
				make function here
				create conference pin, user pin, expert pin
				while checking for duplicates within the day
				and make sure room is unique

				for callback from call in--may need to track callback id (store in db)
				to make sure we track expert vs others and can see when they call in

				'''

		if 'rejectform' in request.POST:
			form = TalkReplyForm(request.POST,instance=reqinstance)
			if form.is_valid():
				instance = form.save(commit=False)

				instance.cancelled = True
				instance.accepted = False
				instance.requested = False
				instance.price = expert.price

				instance.user=request.user
				instance.save()

				return HttpResponseRedirect(reverse('apps.main.views.talkrequests', args=()))	


	context = {'reqtalks':reqtalks , 'talkreplyform': talkreplyform}
	return render(request, 'main/requestedtalks.html', context)	


@twilio_view
def process_pin(request):
	digits_pressed =  request.POST.get('Digits','')

	# conference = Conference.objects.get(pin=digits_pressed)
	# check conference pin and time

	# conftime = conference.talk.time
	# startwindow = 3 hour before call
	# endwindow = 3 hour after call

	# if conftime >= startwindow and conftime <= endwindow:
	# 	were good
	# else:
	# 	dont do call

	r = twiml.Response()
	r.dial(record='record-from-answer',action='/call_hook/').conference(name=digits_pressed)
	return r


@twilio_view
def gather_pin(request, action='/process_pin/', method='POST', num_digits=6, timeout=None,
           finish_on_key=None):

	r = twiml.Response()
	r.say('Welcome to Investor Doyen! Please enter the pin code')
	r.gather(action=action, method=method, numDigits=num_digits,
			timeout=timeout, finishOnKey=finish_on_key)

	return r

@twilio_view
def call_hook(request):

	# digits_pressed =  request.POST.get('Digits','')
	print request.POST




def tos(request):
	return render(request, 'main/tos.html')	

def privacypolicy(request):
	return render(request, 'main/privacypolicy.html')

def faq(request):
	return render(request, 'main/faq.html')	