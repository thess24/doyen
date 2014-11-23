from django.shortcuts import render, get_object_or_404
from apps.main.models import ExpertProfile, Talk, RequestedTalk, Rating, Message
from apps.main.models import RequestedTalkForm, ExpertProfileForm, RatingForm, MessageForm
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from settings.common import MEDIA_ROOT
from django.db.models import Sum
import stripe
import requests

 

def index(request):

	context= {}
	return render(request, 'main/index.html', context)

def expert(request, expertid):
	expert = get_object_or_404(ExpertProfile, id=expertid)
	reviews = Rating.objects.filter(expert_id=expertid)

	requestform = RequestedTalkForm()
	if request.method=='POST':
	# make ajax form here
		if 'requestform' in request.POST:
			form = RequestedTalkForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.expert=expert
				instance.save()

				return HttpResponseRedirect(reverse('apps.main.views.expert', args=()))


	# ratingform = RatingForm()
	# if request.method=='POST':
	## make ajax form here
	# 	if 'ratingform' in request.POST:
	# 		form = RatingForm(request.POST)
	# 		if form.is_valid():
	# 			instance = form.save(commit=False)
	# 			instance.user=request.user
	# 			instance.save()

	# 			return HttpResponseRedirect(reverse('apps.main.views.expertprofile', args=()))


	context = {'expert':expert, 'reviews':reviews, 'requestform':requestform}
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
	print experts
	context = {'experts':experts}
	return render(request, 'main/expertfind.html', context)	

@login_required
def talks(request):
	talks = Talk.objects.filter(user=request.user)
	reqtalks = RequestedTalk.objects.filter(user=request.user)

	context = {'talks':talks, 'reqtalks':reqtalks}
	return render(request, 'main/talks.html', context)	

@login_required
def talkrequests(request):
	reqtalks = RequestedTalk.objects.filter(expert = request.user)

	context = {'reqtalks':reqtalks}
	return render(request, 'main/requestedtalks.html', context)	





def tos(request):
	return render(request, 'main/tos.html')	

def privacypolicy(request):
	return render(request, 'main/privacypolicy.html')

def faq(request):
	return render(request, 'main/faq.html')	