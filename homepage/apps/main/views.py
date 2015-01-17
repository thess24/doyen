from django.shortcuts import render, get_object_or_404, render_to_response
from apps.main.models import ExpertProfile, Talk,TalkTime, Rating, Favorite, UserProfile, CallIn, UserCard
from apps.main.models import TalkForm, TalkTimeForm, ExpertProfileForm, RatingForm, TalkReplyForm
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from settings.common import MEDIA_ROOT
from django.db.models import Sum, Avg, Count
import stripe
import requests
from django.http import HttpResponse, HttpResponseRedirect, Http404
from twilio import twiml
from django_twilio.decorators import twilio_view
from datetime import datetime, timedelta
import uuid, random
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
from django.utils import timezone
from django.forms.models import modelformset_factory
from taggit.models import Tag
from django.contrib import messages
from django.conf import settings



########### UTILS --make new file
def generatepin(talktime, digits=5, expert=False):
	'''expert pins start with 1, user pins start with 0'''

	maxpin = int('9'*digits)

	start_range = talktime - timedelta(days=2)
	end_range = talktime + timedelta(days=2)

	pin = random.randrange(maxpin)
	if expert: 
		pin = "1"+str(pin)
		used_pins = Talk.objects.filter(time__range=[start_range,end_range]).values_list('expert_pin',flat=True)
	else: 
		pin = "0"+str(pin)
		used_pins = Talk.objects.filter(time__range=[start_range,end_range]).values_list('user_pin',flat=True)

	if pin in used_pins:
		generatepin(talktime,expert=expert)

	return pin



def send_html_email(context, subject=None,body=None,to=None, html_path=None, send_at=None):

	msg = EmailMultiAlternatives(
		subject=subject,
		body=body,
		from_email="Investor Doyen <admin@investordoyen.com>",
		to=[to],
		# headers={'Reply-To': "Service <support@example.com>"} # optional extra headers
	)

	c = Context(context)
	htmly = render_to_string(html_path,c)
	msg.attach_alternative(htmly, "text/html")
	# msg.tags = ["one tag", "two tag", "red tag", "blue tag"]
	# msg.metadata = {'user_id': "8675309"}

	if send_at:
		print send_at
		msg.send_at = send_at

	msg.send()






####### Views

def index(request):
	context= {}
	return render(request, 'main/index.html', context)

def emailtest(request):
	# delete once tested
	context= {}
	return render(request, 'account/email_confirm.html', context)


def rateexpert(request, id): #done
	talk = get_object_or_404(Talk, room=id)

	try:
		instance = Rating.objects.get(user=talk.user, expert=talk.expert)
		form = RatingForm(instance=instance)

	except Rating.DoesNotExist:
		form = RatingForm()

	if request.method == "POST":

		try:
			form = RatingForm(request.POST,instance=instance)
		except:
			form = RatingForm(request.POST)

		if form.is_valid():
			instance = form.save(commit=False)
			instance.user = talk.user
			instance.expert = talk.expert
			instance.save()

			messages.success(request, 'Review Submitted!')
			
			return HttpResponseRedirect(reverse('apps.main.views.rateexpert', args=(id,)))
	context= {'talk':talk,'form':form}
	return render(request, 'main/rateexpert.html', context)


def editsettings(request):
	context= {}
	return render(request, 'main/profileeditmain.html', context)

def tagsearch(request,tags):
	taglist = tags.split("+")
	experts = ExpertProfile.objects.filter(tags__name__in=taglist).distinct()
	context = {'experts':experts, 'tags':taglist}
	return render(request, 'main/tagsearch.html', context)	

def requesttalk(request,expertid):
	expert = get_object_or_404(ExpertProfile, id=expertid)
	requestform = TalkForm(prefix='requestform',)
	talktimeform = TalkTimeForm(prefix='talktimeform',)

	if request.method=='POST':
		if 'requestform' in request.POST:
			requestform = TalkForm(request.POST,prefix='requestform')
			talktimeform = TalkTimeForm(request.POST, prefix='talktimeform')

			if requestform.is_valid() and talktimeform.is_valid():
				instance = requestform.save(commit=False)
				instance.expert = expert.user
				instance.user = request.user
				instance.price = expert.price
				instance.save()
				talkid = instance.id

				data = talktimeform.cleaned_data
				for t in ['time1','time2','time3']:
					obj = TalkTime(talk=instance, time= data[t])
					obj.save()


				return HttpResponseRedirect(reverse('apps.main.views.talkpayment', args=(talkid,)))


	context = {'expert':expert,'requestform':requestform, 'talktimeform':talktimeform}
	return render(request, 'main/requesttalk.html',context)


def expert(request, expertid):
	currenttime = timezone.now()

	expert = ExpertProfile.objects.filter(online=True,id=expertid) \
		.annotate(rating_score=Avg('user__rating_expert__rating')) \
		.annotate(rating_count=Count('user__rating_expert__rating'))

	if not expert:
		errortext = 'This expert does not exist'
		return render(request, 'main/error.html', {'errortext': errortext})


	expert = expert[0]

	reviews = Rating.objects.filter(expert_id=expertid)

	if request.user.is_authenticated():
		favorites = Favorite.objects.filter(user=request.user).values_list('expert_id',flat=True)
		finished_talks = Talk.objects.filter(user=request.user,time__lt=currenttime).exclude(accepted_at=None)

		if request.user.id in finished_talks.values_list('user_id',flat=True):
			eligible_to_review = True
			try:
				ratinginstance = Rating.objects.get(user=request.user)
				ratingform = RatingForm(instance=ratinginstance)
			except Rating.DoesNotExist:
				ratingform = RatingForm()

		else:
			eligible_to_review = False
			ratingform = RatingForm()

		requestform = TalkForm()

	else:  # guest user
		eligible_to_review = False
		ratingform = RatingForm()
		requestform = TalkForm()
		favorites = []
		finished_talks = []


	if request.method=='POST':
		if not request.user.is_authenticated():
			raise Http404 # only for backup -- will be handled on frontend

		if 'requestform' in request.POST:
			form = TalkForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.expert = expert.user
				instance.user = request.user
				instance.save()

				return HttpResponseRedirect(reverse('apps.main.views.expert', args=(expertid)))

		if 'ratingform' in request.POST:
			if not eligible_to_review:
				raise Http404
			try:
				form = RatingForm(request.POST,instance=ratinginstance)
			except:
				form = RatingForm(request.POST)

			if form.is_valid():
				instance = form.save(commit=False)
				instance.expert = expert.user
				instance.user = request.user
				instance.save()

				messages.success(request, 'Review Submitted!')
				
				return HttpResponseRedirect(reverse('apps.main.views.expert', args=(expertid)))

			messages.warning(request, "The review didn't work!")

		if 'favorite' in request.POST:

			if expert.id in favorites:
				Favorite.objects.filter(expert=expert.user,user=request.user).delete()
			else:
				favorite = Favorite(expert=expert.user,user=request.user)
				favorite.save()

			return HttpResponseRedirect(reverse('apps.main.views.expert', args=(expertid)))

	context = {'expert':expert,'favorites':favorites, 'reviews':reviews, 'requestform':requestform, 'ratingform':ratingform, 'eligible_to_review':eligible_to_review}
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

				messages.success(request, '''Your profile has successfully been saved.  If this is your first 
					time submitting your expert information, you will be reviewed by Jon 
					before your profile goes online!''')

				return HttpResponseRedirect(reverse('apps.main.views.expertprofile', args=()))

	context= {'expert':expert, 'form':form}
	return render(request, 'main/expertprofile.html', context)	


def expertfind(request):
	experts = ExpertProfile.objects.filter(online=True) \
		.annotate(rating_score=Avg('user__rating_expert__rating')) \
		.annotate(rating_count=Count('user__rating_expert__rating'))


	# User.objects.annotate(rating_score=Avg('rating_expert__rating'))

	# if request.user.is_authenticated:
	# 	favorites = Favorite.objects.filter(user=request.user)
	# else:
	# 	favorites = []

	context = {'experts':experts, 'areacategory':False}
	return render(request, 'main/expertfind.html', context)	

def expertfindcategory(request, category):
	experts = ExpertProfile.objects.filter(online=True,category=category)
	experts_flat = experts.values_list('id',flat=True)
	tags = Tag.objects.filter(expertprofile__id__in=experts_flat)

	if request.user.is_authenticated():
		favorites = Favorite.objects.filter(user=request.user)
	else:
		favorites = []


	# for e in experts:
	# 	print e.tags.all()
	# add these into set or collection and find ones with highest number



	# see taglist -- need to list all tags for people in this category

	context = {'experts':experts, 'areacategory':category, 'tags':tags}
	return render(request, 'main/expertfindcategory.html', context)	

@login_required
def favorites(request):
	favorites = Favorite.objects.filter(user=request.user)

	context = {'favorites':favorites}
	return render(request, 'main/favorites.html', context)

@login_required
def talks(request):

	talks = Talk.objects.filter(user=request.user)
	
	upcomingtalks = talks.filter(user=request.user,time__gt=timezone.now())


	context = {'talks':talks, 'upcomingtalks':upcomingtalks}
	return render(request, 'main/talks.html', context)	


# should add decorator where only experts (online=True) can access or else redirect to forbidden page alert
@login_required
def talkrequests(request):
	expert = get_object_or_404(ExpertProfile, user=request.user)
	talks = Talk.objects.filter(expert = request.user)
	reqtalks = talks.filter(requested=True)
	talktimes = TalkTime.objects.filter(talk__in=reqtalks)
	talkreplyform = TalkReplyForm()

	if request.method=='POST':
		reqid = request.POST.get('requestid','')

		reqinstance = reqtalks.get(id=reqid)
		talk = reqinstance	
		times = TalkTime.objects.filter(talk=talk)

		if 'acceptform' in request.POST:
			talkreplyform = TalkReplyForm(request.POST,instance=reqinstance)

			talktimeid = request.POST.get('talktimeid','')

			if not talktimeid:
				talkreplyform.add_error(None,'Please select a time')

			if talkreplyform.is_valid():

				try: acceptedtime = times.get(id=talktimeid)
				except: raise Http404
				talktime = acceptedtime.time


				instance = talkreplyform.save(commit=False)
				instance.cancelled_at = None
				instance.accepted_at = timezone.now()
				instance.requested = False
				instance.price = expert.price
				instance.room = uuid.uuid4()
				instance.save()

				expertpin = generatepin(talktime,expert=True)
				otherpin = generatepin(talktime)

				talk.expert_pin = expertpin
				talk.user_pin = otherpin

				talk.time = talktime
				talk.save()


				## email out
				c = {'talk':talk}

				send_html_email(c, 
						subject="Investor Doyen - You Accepted an Appointment!",
						body=None,
						to=talk.expert.email, 
						html_path="doyen_email/expert_accept_notify.html"
				)

				send_html_email(c, 
						subject="Investor Doyen - Your Appointment was Accepted!",
						body=None,
						to=talk.user.email, 
						html_path="doyen_email/user_accept_notify.html"
				)

				## reminder emails
				future_time = talk.time - timedelta(days=1)

				send_html_email(c, 
						subject="Investor Doyen - Reminder for your upcoming Appointment!",
						body=None,
						to=talk.expert.email, 
						html_path="doyen_email/expert_reminder.html",
						send_at = future_time
				)

				send_html_email(c, 
						subject="Investor Doyen - Reminder for your upcoming appointment!",
						body=None,
						to=talk.user.email, 
						html_path="doyen_email/user_reminder.html",
						send_at = future_time
				)

				'''
				for callback from call in--may need to track callback id (store in db)
				to make sure we track expert vs others and can see when they call in
				'''

		if 'rejectform' in request.POST:
			form = TalkReplyForm(request.POST,instance=reqinstance)
			if form.is_valid():
				instance = form.save(commit=False)

				instance.cancelled_at = timezone.now()
				instance.accepted_at = None
				instance.requested = False
				instance.price = expert.price

				instance.user=request.user
				instance.save()

				## email out

				c = {'talk':talk, 'times':times}
				send_html_email(c, 
						subject="Investor Doyen - Your appointment has been declined",
						body=None,
						to=talk.user.email, 
						html_path="doyen_email/user_reject_notify.html"
				)

				return HttpResponseRedirect(reverse('apps.main.views.talkrequests', args=()))	


	context = {'reqtalks':reqtalks , 'talkreplyform': talkreplyform, 'talktimes':talktimes, 'talks':talks}
	return render(request, 'main/requestedtalks.html', context)	


##### Call routing #####

@twilio_view
def process_pin(request):
	digits_pressed = request.POST.get('Digits','')
	callkey = request.POST.get('CallSid','')

	leaddigit = digits_pressed[0]
	currenttime = timezone.now()

	starttime = currenttime - timedelta(hours=3)
	endtime = currenttime + timedelta(hours=4)

	if leaddigit == "1":
		expert = True
		user = False

	elif leaddigit == "0":
		expert = False
		user = True


	if expert:
		talk = Talk.objects.get(expert_pin=digits_pressed) #filter by date
		if not starttime < talk.time < endtime:
			r = twiml.Response()
			r.say('Please call back within a reasonable window for you appointment')
			return r

		talk.expert_count = 1

		call = CallIn(talk=talk,twilio_call_key=callkey,expert=True)
		call.save()

	elif user:
		talk = Talk.objects.get(user_pin=digits_pressed) #filter by date
		if not starttime < talk.time < endtime:
			r = twiml.Response()
			r.say('Please call back within a reasonable window for you appointment')
			return r

		talk.user_count+=1

		call = CallIn(talk=talk,twilio_call_key=callkey)
		call.save()


	else:
		# should go to another view that says error, then directs to gather_pin()
		r = twiml.Response()
		r.say('Sorry, your pin code is invalid. Goodbye.')
		return r
		# return HttpResponseRedirect(reverse('apps.main.views.gather_pin', args=()))



	if talk.expert_count == 1 and talk.user_count >= 1 and not talk.time_started:
		talk.time_started = timezone.now()



	talk.save()
	r = twiml.Response()
	r.dial(action='/call_hook/').conference(name=talk.room)
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

	callkey = request.POST.get('CallSid','')
	callin = CallIn.objects.get(twilio_call_key=callkey)
	callin.time_ended = timezone.now()
	callin.save()

	talk = callin.talk

	if callin.expert == True:
		talk.expert_count=0
	else: 
		talk.user_count-=1

	if talk.expert_count == 0 and talk.time_started and not talk.time_ended:
		talk.time_ended = timezone.now()
		talk.completed = True

		c = {'talk':talk}
		send_html_email(c, 
				subject="Investor Doyen - Appointment Completed!",
				body=None,
				to=talk.expert.email, 
				html_path="doyen_email/expert_payment.html"
			)

		send_html_email(c, 
				subject="Investor Doyen - Please Rate!",
				body=None,
				to=talk.user.email, 
				html_path="doyen_email/user_rate_expert.html"
			)

		send_html_email(c, 
				subject="Investor Doyen - Invoice",
				body=None,
				to=talk.user.email, 
				html_path="doyen_email/user_invoice.html"
			)
		
	elif talk.expert_count == 1 and talk.time_started and talk.user_count == 0 and not talk.time_ended:
		talk.time_ended = timezone.now()
		talk.completed = True

		c = {'talk':talk}
		send_html_email(c, 
				subject="Investor Doyen - Talk Completed!",
				body=None,
				to=talk.expert.email, 
				html_path="doyen_email/expert_payment.html"
			)

		send_html_email(c, 
				subject="Investor Doyen - Please Rate!",
				body=None,
				to=talk.user.email, 
				html_path="doyen_email/user_rate_expert.html"
			)

		send_html_email(c, 
				subject="Investor Doyen - Invoice",
				body=None,
				to=talk.user.email, 
				html_path="doyen_email/user_invoice.html"
			)

	talk.save()



##### checkout flow #####
def talkpayment(request, talkid):
	talk = Talk.objects.get(id=talkid)

	if not talk.requested:
		errortext = 'You cannot change the payment option after the request has been approved'
		return render(request, 'main/error.html', {'errortext': errortext})


	talktimes = TalkTime.objects.filter(talk=talk)

	stripe.api_key= settings.STRIPE_API_KEY 
	newcustomer, created = UserProfile.objects.get_or_create(user=request.user)

	user_cards = UserCard.objects.filter(user=request.user) # get all cards on file
	default_card = newcustomer.default_card 

	if request.method == "POST":
		if 'usecard' in request.POST:
			# check card here to see if it works, then add to talk

			card_id = request.POST.get('card_id','')
			if not card_id:
				messages.warning(request,'Please select a card!')
				return HttpResponseRedirect(reverse('apps.main.views.talkpayment', args=(talkid,)))

			selected_card = user_cards.get(id=card_id)

			customer = stripe.Customer.retrieve(newcustomer.stripe_id)
			card = customer.cards.retrieve(selected_card.stripe_id)
			card.name = selected_card.name
			try:
				card.save()
			except stripe.CardError,e:
				messages.warning(request,'Your card is not valid')
				return HttpResponseRedirect(reverse('apps.main.views.talkpayment', args=(talkid,)))

			talk.card = selected_card
			talk.save()
			return HttpResponseRedirect(reverse('apps.main.views.review', args=(talkid,)))

		
		else:
			token = request.POST.get('stripeToken')

			if not newcustomer.stripe_id:  
				# create customer if user submits card and doesnt have a stripeid on file
				customer = stripe.Customer.create(
					card=token,
					email=request.user.email
				)

				newcustomer.stripe_id = customer.id
				card = customer.cards.retrieve(customer.default_card) #should be the card just submitted

			else:  
				# if they already have a stripe account
				customer = stripe.Customer.retrieve(newcustomer.stripe_id)

				try:
					card = customer.cards.create(card=token)
				except stripe.CardError, e:
					messages.warning(request,'Your card is not valid')
					return HttpResponseRedirect(reverse('apps.main.views.talkpayment', args=(talkid,)))



			newcard = UserCard(
							user = request.user,
							name = card.name,
							brand = card.brand,
							last4 = card.last4,
							exp_month = card.exp_month,
							exp_year = card.exp_year,
							stripe_id = card.id
							)
			newcard.save()

			# newcustomer = UserProfile.objects.get(user=request.user)
			newcustomer.default_card = newcard
			newcustomer.save()

			return HttpResponseRedirect(reverse('apps.main.views.talkpayment', args=(talkid,)))



	context = {'talk':talk, 'user_cards':user_cards, 'default_card':default_card, 'talktimes':talktimes, 'stripekey':settings.STRIPE_PUBLISHABLE_KEY}
	return render(request, 'main/talkpayment.html', context)




def review(request, talkid):
	# make sure there is a valid card on file before allowing to access this page,
	#    or note that there needs to be a card on file and dont let submit
	talk = Talk.objects.get(id=talkid)

	times = TalkTime.objects.filter(talk=talk)

	if request.method == 'POST':
		if 'order' in request.POST:
			talk.requested = True
			talk.save()

			## email out
			c = {'talk':talk, 'times': times}
			send_html_email(c, 
					subject="Investor Doyen - You requested a talk",
					body=None,
					to=talk.user.email, 
					html_path="doyen_email/user_request_notify.html"
			)
			send_html_email(c, 
					subject="Investor Doyen - Someone requested a talk!",
					body=None,
					to=talk.expert.email, 
					html_path="doyen_email/expert_request_notify.html"
			)


			context = {'talk':talk}
			return render(request, 'main/orderconfirm.html', context)	


	context = {'talk':talk}
	return render(request, 'main/review.html', context)	


def invoice(request):

	context = {}
	return render(request, 'main/invoice.html', context)	

def chargedashboard(request):
	if not request.user.is_superuser:
		raise Http404

	talks = Talk.objects.filter(completed=True,paid_at=None)
	if request.method == "POST":
		talk_id = request.POST.get('talk_id','')  
		# error handling here
		talk = talks.get(id=talk_id)
		cost_in_cents = talk.cost() * 100

		customer_id = talk.user.userprofile.stripe_id
		card_id = talk.card.stripe_id

		# https://stripe.com/docs/api#create_charge
		stripe.api_key= settings.STRIPE_API_KEY 

		try:
			charge = stripe.Charge.create(
				amount=int(cost_in_cents), # amount in cents
				currency="usd",
				customer=customer_id,
				card=card_id,
				description= talk.expert.get_full_name()
			)
		except stripe.CardError, e:
			messages.warning(request,'The card is not valid')
			return HttpResponseRedirect(reverse('apps.main.views.chargedashboard', args=()))

		talk.paid_at = timezone.now()
		talk.save()



	context = {'talks':talks}
	return render(request, 'main/chargedashboard.html', context)	



def tos(request):
	return render(request, 'main/tos.html')	

def privacypolicy(request):
	return render(request, 'main/privacypolicy.html')

def faq(request):
	return render(request, 'main/faq.html')	

def about(request):
	return render(request, 'main/about.html')	