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
from django.http import HttpResponse, HttpResponseRedirect, Http404
import pytz # time zones
from timezone_field import TimeZoneField

 


class UserCard(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=150)
	brand = models.CharField(max_length=100)
	last4 = models.CharField(max_length=4)
	exp_month = models.CharField(max_length=2)
	exp_year = models.CharField(max_length=4)
	last_used = models.DateTimeField(auto_now=True)
	stripe_id = models.CharField(max_length=100)
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return "{} - {}".format(self.user.email, self.last4)


class UserProfile(models.Model):
	user = models.OneToOneField(User)
	stripe_id = models.CharField(max_length=200)  
	picture = models.ImageField(upload_to='profilepics')
	default_card = models.ForeignKey(UserCard, blank=True,null=True)

	def __unicode__(self):
		return self.user.email


class ExpertProfile(models.Model):
	user = models.OneToOneField(User)
	short_bio = models.TextField()  
	resume = models.TextField()  
	price = models.DecimalField(max_digits=6, decimal_places=2)
	picture = models.ImageField(upload_to='profilepics')
	online = models.BooleanField(default=False)
	title = models.CharField(max_length=100)
	time_zone = TimeZoneField()
	location = models.CharField(max_length=100)
	twitter = models.CharField(max_length=50, blank=True, null=True)
	linkedin = models.CharField(max_length=50, blank=True, null=True)
	category = models.CharField(max_length=100)
	
	# add stripe connect info?

	tags = TaggableManager()

	def __unicode__(self):
		return "{}- {}".format(self.user.id, self.user.email)


class Talk(models.Model):
	user = models.ForeignKey(User, related_name='talk_user')
	expert = models.ForeignKey(User, related_name='talk_expert')
	time = models.DateTimeField(blank=True,null=True)
	created = models.DateTimeField(auto_now_add=True)
	price = models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
	room = models.CharField(max_length=100,blank=True,null=True)
	message = models.TextField(max_length=500, blank=True, null=True)
	reply_message = models.TextField(max_length=500, blank=True, null=True)
	time_estimated = models.IntegerField(default=0)

	accepted_at = models.DateTimeField(blank=True,null=True)
	cancelled_at = models.DateTimeField(blank=True,null=True)
	requested = models.BooleanField(default=True)

	expert_pin = models.CharField(max_length=10,blank=True,null=True)
	user_pin = models.CharField(max_length=10,blank=True,null=True)
	expert_count = models.IntegerField(default=0)
	user_count = models.IntegerField(default=0)

	disconnected = models.DateTimeField(blank=True,null=True)

	time_started = models.DateTimeField(blank=True,null=True)
	time_ended = models.DateTimeField(blank=True,null=True)
	completed = models.BooleanField(default=False)

	paid_at = models.DateTimeField(blank=True,null=True)
	card = models.ForeignKey(UserCard,blank=True,null=True)


	def accepted(self):
		"""returns whether the expert has accepted or not"""
		if self.accepted_at is None:
			return False
		return True

	def cancelled(self):
		"""returns whether the recipient has read the message or not"""
		if self.cancelled_at is None:
			return False
		return True

	def call_length(self):
		start = self.time_started
		end = self.time_ended

		if start==None or end==None:
			return 0
		else:
			delta = end-start
			minutes = delta.seconds/60

			return minutes

	def cost(self):
		return self.call_length * self.price

	def __unicode__(self):
		return '{} - {}'.format(self.id,self.user.email)


class TalkTime(models.Model):
	talk = models.ForeignKey(Talk, blank=True,null=True)
	time = models.DateTimeField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return str(self.time)


class Rating(models.Model):
	user = models.ForeignKey(User, related_name='rating_user')
	expert = models.ForeignKey(User, related_name='rating_expert')
	rating = models.IntegerField()
	comment = models.TextField()
	title = models.CharField(max_length=100)
	date = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.expert.email


class ConferenceLine(models.Model):
	pin = models.CharField(max_length=10)
	talk = models.ForeignKey(Talk, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	expert = models.BooleanField(default=False)


	def __unicode__(self):
		return self.pin    


class CallIn(models.Model):
	twilio_call_key = models.CharField(max_length=100)
	talk = models.ForeignKey(Talk)
	time_started = models.DateTimeField(auto_now_add=True)
	time_ended = models.DateTimeField(blank=True,null=True)
	expert = models.BooleanField(default=False)

	def __unicode__(self):
		return self.talk.user.email    


class Favorite(models.Model):
	user = models.ForeignKey(User, related_name='favorite_user')
	expert = models.ForeignKey(User, related_name='favorite_expert')
	created_at = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.user.email    



##########    FORMS   ############

class ExpertProfileForm(ModelForm):
	class Meta:
		model = ExpertProfile
		exclude = ['user', 'online']

	def __init__(self, *args, **kwargs):
		super(ExpertProfileForm, self).__init__(*args, **kwargs)
		self.helper= FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_id = 'upload-form'
		self.helper.label_class = 'col-lg-3'
		self.helper.field_class = 'col-lg-9'
		self.helper.layout = Layout(
				'short_bio' ,
				'resume' ,
				'title',
				'time_zone',
				'location',
				'price' ,
				'tags',
				'picture',
				'category',
				'twitter',
				'linkedin',
				StrictButton('Submit', name='updateprofile', type='submit',css_class='btn-primary btn-lg'),
		)


class TalkForm(ModelForm):
	class Meta:
		model = Talk
		fields = ['message']
		# widgets = {
		# 	'name': Textarea(attrs={'class':'form-control'}),
		# }

	# def __init__(self, *args, **kwargs):
	# 	super(TalkForm, self).__init__(*args, **kwargs)
	# 	self.helper= FormHelper()
	# 	self.helper.form_class = 'form-horizontal'
	# 	self.helper.form_id = 'upload-form'
	# 	self.helper.label_class = 'col-lg-3'
	# 	self.helper.field_class = 'col-lg-9'
	# 	self.helper.layout = Layout(
	# 			'message' ,
	# 			StrictButton('Submit', name='requestform', type='submit',css_class='btn-primary btn-lg'),
	# 	)

class TalkTimeForm(forms.Form):
    time1 = forms.DateTimeField(widget=forms.TextInput(attrs={'class': 'datetimefield form-control'}))
    time2 = forms.DateTimeField(widget=forms.TextInput(attrs={'class': 'datetimefield form-control'}))
    time3 = forms.DateTimeField(widget=forms.TextInput(attrs={'class': 'datetimefield form-control'}))



class TalkReplyForm(ModelForm):
	class Meta:
		model = Talk
		fields = ['reply_message']

	def __init__(self, *args, **kwargs):
		super(TalkReplyForm, self).__init__(*args, **kwargs)
		self.helper= FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_id = 'upload-form'
		self.helper.label_class = 'col-lg-3'
		self.helper.field_class = 'col-lg-9'
		self.helper.layout = Layout(
				'reply_message' ,
				StrictButton('Submit', name='requestform', type='submit',css_class='btn-primary btn-lg'),
		)

class RatingForm(ModelForm):
	class Meta:
		model = Rating
		exclude = ['user', 'expert', 'date']

	def __init__(self, *args, **kwargs):
		super(RatingForm, self).__init__(*args, **kwargs)
		self.helper= FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_id = 'upload-form'
		self.helper.label_class = 'col-lg-3'
		self.helper.field_class = 'col-lg-9'
		self.helper.layout = Layout(
				'title' ,
				'rating' ,
				'comment' ,
				# StrictButton('Submit', name='ratingform', type='submit',css_class='btn-primary btn-lg'),
		)


# extended form for allauth
class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='First Name', required=True)
    last_name = forms.CharField(max_length=30, label='Last Name', required=True)

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

