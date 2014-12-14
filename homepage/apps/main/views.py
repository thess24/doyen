from django.shortcuts import render, get_object_or_404
from apps.main.models import ExpertProfile, Talk, Rating, Message, Favorite, UserProfile, ConferenceLine, CallIn
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
from datetime import datetime
import uuid
import random
from django.core.mail import EmailMultiAlternatives


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

def requesttalk(request,expertid):
	expert = get_object_or_404(ExpertProfile, id=expertid)
	requestform = TalkForm()

	if request.method=='POST':
	# make ajax form here, also make sure user signed up
		if 'requestform' in request.POST:
			form = TalkForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.expert = expert.user
				instance.user = request.user
				instance.save()

				talkid = str(instance.id)

				return HttpResponseRedirect(reverse('apps.main.views.talkpayment', args=(talkid)))
	
	context = {'expert':expert,'requestform':requestform}
	return render(request, 'main/requesttalk.html',context)


def expert(request, expertid):
	currenttime = datetime.now()

	expert = get_object_or_404(ExpertProfile, id=expertid)
	reviews = Rating.objects.filter(expert_id=expertid)
	favorites = Favorite.objects.filter(user=request.user).values_list('expert_id',flat=True)
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

				return HttpResponseRedirect(reverse('apps.main.views.expert', args=(expertid)))

		if 'sendmessage' in request.POST:
			form = MessageForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.reciever = expert.user
				instance.sender = request.user
				instance.save()

				return HttpResponseRedirect(reverse('apps.main.views.expert', args=(expertid)))

		if 'ratingform' in request.POST:
			form = RatingForm(request.POST)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.expert = expert.user
				instance.user=request.user
				instance.save()

				return HttpResponseRedirect(reverse('apps.main.views.expert', args=(expertid)))

		if 'favorite' in request.POST:

			if expert.id in favorites:
				Favorite.objects.filter(expert=expert.user,user=request.user).delete()
			else:
				favorite = Favorite(expert=expert.user,user=request.user)
				favorite.save()

			return HttpResponseRedirect(reverse('apps.main.views.expert', args=(expertid)))

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


	form = MessageForm()

	# if request.method=='POST':
	# 	if 'sendmessage' in request.POST:
	# 		form = ExpertProfileForm(request.POST)
	# 		if form.is_valid():
	# 			instance = form.save(commit=False)
	# 			instance.user=request.user
	# 			instance.save()

	# 			return HttpResponseRedirect(reverse('apps.main.views.messages', args=()))	


	context = {'inbox':inbox,'outbox':outbox, 'form':form}
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
def favorites(request):
	favorites = Favorite.objects.filter(user=request.user)

	context = {'favorites':favorites}
	return render(request, 'main/favorites.html', context)

@login_required
def talks(request):

	# only times for future
	# revise for fewer queries
	# talks = Talk.objects.filter(user=request.user,time__gt=datetime.now()).exclude(accepted_at=None)
	talks = Talk.objects.filter(user=request.user).exclude(accepted_at=None)
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

				instance.save()


				talk = Talk.objects.get(id=reqid)


				expertpin = generatepin(expert=True)
				otherpin = generatepin()

				talk.expert_pin = expertpin
				talk.user_pin = otherpin

				talk.save()



				msg = EmailMultiAlternatives(
					subject="Your Talk was Accepted!",
					body="This is the text email body",
					from_email="Investor Doyen <admin@investordoyen.com>",
					to=[talk.user.email],
					headers={'Reply-To': "Service <support@example.com>"} # optional extra headers
				)
				c = Context({})
				htmly = render_to_string("user_accept_notify.html",c)

				msg.attach_alternative(htmly, "text/html")
				# msg.tags = ["one tag", "two tag", "red tag", "blue tag"]
				# msg.metadata = {'user_id': "8675309"}
				msg.send()


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


##### Call routing #####

@twilio_view
def process_pin(request):
	digits_pressed = request.POST.get('Digits','')
	callkey = request.POST.get('CallSid','')

	leaddigit = digits_pressed[0]

	if leaddigit == "1":
		expert = True
		user = False

	elif leaddigit == "0":
		expert = False
		user = True


	if expert:
		talk = Talk.objects.get(expert_pin=digits_pressed) #filter by date
		## if error go back to enter digit prompt
		talk.expert_count = 1

		call = CallIn(talk=talk,twilio_call_key=callkey,expert=True)
		call.save()

	elif user:
		talk = Talk.objects.get(user_pin=digits_pressed) #filter by date
		## if error go back to enter digit prompt
		talk.user_count+=1

		call = CallIn(talk=talk,twilio_call_key=callkey)
		call.save()


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



	talk.save()
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

	callkey = request.POST.get('CallSid','')
	callin = CallIn.objects.get(twilio_call_key=callkey)
	callin.time_ended = datetime.now()
	callin.save()

	talk = callin.talk

	if callin.expert == True:
		talk.expert_count=0
	else: 
		talk.user_count-=1

	if talk.expert_count == 0 and talk.time_started and not talk.time_ended:
		talk.time_ended = datetime.now()
	elif talk.expert_count == 1 and talk.time_started and talk.user_count == 0 and not talk.time_ended:
		talk.time_ended = datetime.now()


	talk.save()

	print request.POST


##### checkout flow #####
def talkpayment(request, talkid):
	talk = Talk.objects.get(id=talkid)

	stripe.api_key= 'sk_test_9ucD3dSakYLAivmgxMqOJd0r'  #test keys -- change to env var in prod
	newcustomer, created = UserProfile.objects.get_or_create(user=request.user)

	if newcustomer.stripe_id:
		customer = stripe.Customer.retrieve(newcustomer.stripe_id)
		card = customer.cards.retrieve(customer.default_card)

	if request.method == "POST":
		token = request.POST.get('stripeToken')

		customer = stripe.Customer.create(
			card=token,
			description=request.user.email
		)

		card = customer.cards.retrieve(customer.default_card)


		newcustomer, created = UserProfile.objects.get_or_create(user=request.user)
		newcustomer.stripe_id = customer.id
		newcustomer.save()
		context = {'card':card, 'talk':talk}



	context = {'talk':talk}
	return render(request, 'main/talkpayment.html', context)



def payment(request):
	''' if customer has submitted card before, displays card on file
		if they havent, it gets info from them '''


	# need to:
	# add card model to store cards for user
	# add card fk for talk to know what card to charge
	# handle errors
	# add button to move to review page, also add selected/inputted card to talk model instance
	# BEFORE PROD - change api key to real one and make env variable


	stripe.api_key= 'sk_test_9ucD3dSakYLAivmgxMqOJd0r'  #test keys -- change to env var in prod
	newcustomer, created = UserProfile.objects.get_or_create(user=request.user)

	if newcustomer.stripe_id:
		customer = stripe.Customer.retrieve(newcustomer.stripe_id)
		card = customer.cards.retrieve(customer.default_card)

	if request.method == "POST":
		token = request.POST.get('stripeToken')

		customer = stripe.Customer.create(
			card=token,
			description=request.user.email
		)

		card = customer.cards.retrieve(customer.default_card)


		newcustomer, created = UserProfile.objects.get_or_create(user=request.user)
		newcustomer.stripe_id = customer.id
		newcustomer.save()


	context = {'card':card}
	return render(request, 'main/payment.html', context)	


def review(request, talkid):
	talk = Talk.objects.get(id=talkid)

	if request.method == 'POST':
		if 'order' in request.POST:
			talk.requested = True
			talk.save()

			context = {'talk':talk}
			return render(request, 'main/orderconfirm.html', context)	


	context = {'talk':talk}
	return render(request, 'main/review.html', context)	


def invoice(request):

	context = {}
	return render(request, 'main/invoice.html', context)	


def charge(request):
	# # stripe.api_key = "sk_test_9ucD3dSakYLAivmgxMqOJd0r"  #only for universal, this is a marketplace so every vendor has their own

	# talk = Talk.objects.get(id=)
	# price = talk.cost * 100

	# customer_id = talk.user.userprofile.stripe_id
	# card_id = talk.user.card

	## https://stripe.com/docs/api#create_charge
	## should pass customer and card

	# try:
	# 	charge = stripe.Charge.create(
	# 		amount= price, # amount in cents, again
	# 		currency="usd",
	# 		customer=customer_id,
	#		card=card_id,
	# 		description= talk.expert.get_full_name()
	# 	)
	# except stripe.CardError, e:
	# 	# The card has been declined
	# 	raise Http404

	return render(request, 'main/invoice.html', context)




	# # Set your secret key: remember to change this to your live secret key in production
	# # See your keys here https://manage.stripe.com/account
	# # stripe.api_key = "sk_test_BQokikJOvBiI2HlWgH4olfQ2"  #only for universal, this is a marketplace so every vendor has their own

	# token = request.POST.get('stripeToken')
	# email = request.POST.get('stripeEmail')
	# try:productid = request.POST['productid']
	# except: raise Http404  #put better error here

	# product = Product.objects.get(id=productid)
	# product_price = product.price
	# product_amt = product_price*100
	# mycut = product_amt*3/10

	# a,b = UserProfile.objects.get_or_create(user=request.user)
	# publishkey = product.user_created.userprofile.stripe_publishable_key
	# accesstoken = product.user_created.userprofile.access_token


	# try:
	# 	charge = stripe.Charge.create(
	# 		amount=product_amt, 
	# 		currency="usd",
	# 		card=token,
	# 		description=email,
	# 		application_fee= mycut,
	# 		api_key = accesstoken,
	# 	)
	# except stripe.CardError, e:
	#   # The card has been declined
	#   # render error template
	# 	pass


	# # create purchase record
	# if request.user.is_authenticated():
	# 	purchase = Purchase(user=request.user, price=product_price, product=product, email=email, downloads=5, uuid=str(uuid.uuid4()))
	# else:
	# 	purchase = Purchase(product=product, price=product_price ,email=email, downloads=5, uuid=str(uuid.uuid4()))
	# purchase.save()


	# product.purchases+=1
	# product.save()

	# # send email
	# plaintext = get_template('downloademail.txt')
	# htmly = get_template('downloademail.html')
	# d = Context({ 'purchase': purchase })
	# subject, from_email, to = 'Download Link', 'from@example.com', 'thess624@gmail.com'
	# text_content = plaintext.render(d)
	# html_content = htmly.render(d)
	# msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
	# msg.attach_alternative(html_content, "text/html")
	# msg.send()


	# context= {'purchase':purchase}
	# return render(request, 'main/success.html', context)




	# # Save the customer ID in your database so you can use it later
	# save_stripe_customer_id(user, customer.id)

	# # Later...
	# customer_id = get_stripe_customer_id(user)

	# stripe.Charge.create(
	#     amount=1500, # $15.00 this time
	#     currency="usd",
	#     customer=customer_id
	# )


	# Create the charge on Stripe's servers - this will charge the user's card
	# try:
	# 	charge = stripe.Charge.create(
	# 		amount=ticektscents, # amount in cents, again
	# 		currency="usd",
	# 		customer=customer_id,
	# 		# card=token,
	# 		description="payinguser@example.com"
	# 	)
	# except stripe.CardError, e:
	# 	# The card has been declined
	# 	raise Http404



def tos(request):
	return render(request, 'main/tos.html')	

def privacypolicy(request):
	return render(request, 'main/privacypolicy.html')

def faq(request):
	return render(request, 'main/faq.html')	