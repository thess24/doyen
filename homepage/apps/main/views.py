from django.shortcuts import render, get_object_or_404
from apps.main.models import ExpertProfile, Talk, RequestedTalk
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


def tos(request):
	return render(request, 'main/tos.html')	

def privacypolicy(request):
	return render(request, 'main/privacypolicy.html')

def faq(request):
	return render(request, 'main/faq.html')	