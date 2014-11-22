from django.shortcuts import render, get_object_or_404
from apps.main.models import ExpertProfile, Talk, RequestedTalk, Rating
from apps.main.models import RequestedTalkForm, ExpertProfileForm, RatingForm
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from settings.common import MEDIA_ROOT
from django.db.models import Sum
import stripe
import requests

 

def index(request):
	# products = Product.objects.filter(active=True)

	# if request.method == "GET":
	# 	if request.GET.get('type'):
	# 		sorttype = request.GET.get('type')
	# 		if not sorttype in ['popular', 'featured', 'recent']: raise Http404

	# 		if sorttype=='popular': 
	# 			products.order_by('purchases','-added_date')
	# 		if sorttype=='featured': 
	# 			products.order_by('featured','-added_date')
	# 		if sorttype=='recent': 
	# 			products.order_by('-added_date')

	context= {}
	return render(request, 'main/index.html', context)

def expert(request, expertid):
	# expert = ExpertProfile.objects.get(id=expertid)

	context = {}
	return render(request, 'main/expert.html')	

def expertprofile(request):
	try: expert = ExpertProfile.objects.get(user=request.user)
	except: expert = None

	form = ExpertProfileForm(instance=expert)

	if request.method=='POST':
		if 'updateprofile' in request.POST:
			form = ExpertProfileForm(request.POST, instance=expert)
			if form.is_valid():
				instance = form.save(commit=False)
				instance.user=request.user
				instance.save()

				return HttpResponseRedirect(reverse('apps.main.views.expertprofile', args=()))

	context= {'expert':expert, 'form':form}
	return render(request, 'main/expertprofile.html', context)	

def expertfind(request):
	expert = ExpertProfile.objects.all()

	context ={expert:'expert'}
	return render(request, 'main/expertfind.html', context)	

def talks(request):
	return render(request, 'main/talks.html')	

def talkrequests(request):
	# reqtalks = RequestedTalk.objects.filter(expert = request.user)

	# context = {reqtalks:'reqtalks'}
	return render(request, 'main/requestedtalks.html')	

def tos(request):
	return render(request, 'main/tos.html')	

def privacypolicy(request):
	return render(request, 'main/privacypolicy.html')

def faq(request):
	return render(request, 'main/faq.html')	