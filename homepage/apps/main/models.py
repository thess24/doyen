from django.db import models
from django.forms import ModelForm, Textarea
from django import forms
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
import os
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from crispy_forms.bootstrap import PrependedText, StrictButton
from django.core.exceptions import ValidationError

# class ProductImage(models.Model):
# 	product = models.ForeignKey(Product)
# 	text = models.CharField(max_length=140,blank=True, null=True)
# 	added_date = models.DateTimeField(auto_now_add=True)
# 	image = models.ImageField(upload_to='products')
  
# 	def __unicode__(self):
# 		return self.product.name

# class Purchase(models.Model):
# 	user = models.ForeignKey(User, blank=True, null=True)
# 	product = models.ForeignKey(Product)
# 	sale_date = models.DateTimeField(auto_now_add=True)
# 	downloads = models.IntegerField()
# 	email = models.EmailField()
# 	uuid = models.CharField(max_length=100)
# 	price = models.DecimalField(max_digits=6, decimal_places=2)

# 	def active_to_download(self):
# 		if self.downloads <=0: return False
# 		else: return True

# 	def __unicode__(self):
# 		return self.product.name



class ExpertProfile(models.Model):
	user = models.OneToOneField(User)
	credentials = models.CharField(max_length=1000)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	picture = models.ImageField(upload_to='profilepics')
	online = models.BooleanField(default=False)

	tags = TaggableManager()

	def __unicode__(self):
		return self.user.email


class Talk(models.Model):
	user = models.ForeignKey(User, related_name='talk_user')
	expert = models.ForeignKey(User, related_name='talk_expert')
	time = models.DateTimeField()
	created = models.DateTimeField(auto_now_add=True)
	price = models.DecimalField(max_digits=6, decimal_places=2)

	def __unicode__(self):
		return self.created


class RequestedTalk(models.Model):
	user = models.ForeignKey(User, related_name='reqtalk_user')
	expert = models.ForeignKey(User, related_name='reqtalk_expert')
	time = models.DateTimeField()
	message = models.CharField(max_length=1000)
	created = models.DateTimeField(auto_now_add=True)
	new = models.BooleanField(default=True)

	def __unicode__(self):
		return self.expert.email
		

# model for messaging btwn expert and user
# 3 times to ask expert about -- request for talk
# saved experts
# user extension to store stripe creds
