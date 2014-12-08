from django.shortcuts import render, get_object_or_404
from apps.main.models import ExpertProfile, Talk, Rating, Message, Favorite, UserProfile, ConferenceLine
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
# import datetime  # arrow? 
from datetime import datetime
import uuid
import random

########### UTILS --make new file
def generatepin(digits=6, expert=False):
	'''expert pins start with 1, user pins start with 0'''

	maxpin = int('9'*digits)
	used_pins = ConferenceLine.objects.values_list('pin',flat=True)
	# filter on time here--none in same 3 day span



	pin = random.randrange(maxpin)
	if expert: pin = int("1"+str(pin))
	else: pin = int("0"+str(pin))

	if pin in used_pins:
		generatepin()

	return pin






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
	currenttime = datetime.now()

	expert = get_object_or_404(ExpertProfile, id=expertid)
	reviews = Rating.objects.filter(expert_id=expertid)
	favorites = Favorite.objects.filter(user=request.user)
	finished_talks = Talk.objects.filter(user=request.user,time__gt=currenttime).exclude(accepted_at=None)
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
	talks = Talk.objects.filter(user=request.user,time__gt=datetime.now()).exclude(accepted_at=None)
	# talks = Talk.objects.filter(user=request.user, accepted=True)
	reqtalks = Talk.objects.filter(user=request.user)


	context = {'talks':talks, 'reqtalks':reqtalks}
	return render(request, 'main/talks.html', context)	


# should add decorator where only experts can access or else redirect to forbidden page alert
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

				instance.cancelled_at = None
				instance.accepted_at = datetime.now()
				instance.requested = False
				instance.price = expert.price
				instance.room = uuid.uuid4()

				instance.user=request.user
				instance.save()


				talk = Talk.objects.get(id=reqid)


				expertpin = generatepin(expert=True)
				otherpin = generatepin()

				print expertpin
				print otherpin

				talk.expert_pin = expertpin
				talk.user_pin = otherpin

				'''
				for callback from call in--may need to track callback id (store in db)
				to make sure we track expert vs others and can see when they call in
				'''

		if 'rejectform' in request.POST:
			form = TalkReplyForm(request.POST,instance=reqinstance)
			if form.is_valid():
				instance = form.save(commit=False)

				instance.cancelled_at = datetime.now()
				instance.accepted_at = None
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

	leaddigit = digits_pressed[0]

	if leaddigit == "1":
		expert = True
		user = False

	elif leaddigit == "0":
		expert = False
		user = True


	if expert:
		talk = Talk.objects.get(expert_pin=int(digits_pressed))
		## if error go back to enter digit prompt
		talk.expert_count = 1


	elif user:
		talk = Talk.objects.get(user_pin=int(digits_pressed))
		## if error go back to enter digit prompt
		talk.user_count+=1


	else:
		## redirect to pin prompt
		pass

	## check times here and see if its within window
		# conftime = conference.talk.time
		# startwindow = 3 hour before call
		# endwindow = 3 hour after call

		# if conftime >= startwindow and conftime <= endwindow:
		# 	were good
		# else:
		# 	dont do call


	if talk.expert_count == 1 and talk.user_count >= 1 and not talk.time_started:
		talk.time_started = datetime.now()




	r = twiml.Response()
	r.dial(action='/call_hook/').conference(name=talk.room)
	# r.dial(record='record-from-answer',action='/call_hook/').conference(name=digits_pressed)
	return r


@twilio_view
def gather_pin(request, action='/process_pin/', method='POST', num_digits=6, timeout=None,
           finish_on_key=None):

	r = twiml.Response()
	r.say('Welcome to Investor Doyen! Please enter your pin code')
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