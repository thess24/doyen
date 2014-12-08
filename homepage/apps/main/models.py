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


class UserProfile(models.Model):
	user = models.OneToOneField(User)
	stripe_id = models.CharField(max_length=200)  
	picture = models.ImageField(upload_to='profilepics')

	def __unicode__(self):
		return self.user.email


class ExpertProfile(models.Model):
	user = models.OneToOneField(User)
	qualifications = models.TextField()  
	price = models.DecimalField(max_digits=6, decimal_places=2)
	picture = models.ImageField(upload_to='profilepics')
	online = models.BooleanField(default=False)
	title = models.CharField(max_length=100)
	time_zone = TimeZoneField()
	location = models.CharField(max_length=100)
	twitter = models.CharField(max_length=50, blank=True, null=True)
	linkedin = models.CharField(max_length=50, blank=True, null=True)
	# categories = models.   Many to Many

	tags = TaggableManager()

	def __unicode__(self):
		return self.user.email


class Talk(models.Model):
	user = models.ForeignKey(User, related_name='talk_user')
	expert = models.ForeignKey(User, related_name='talk_expert')
	time = models.DateTimeField()
	created = models.DateTimeField(auto_now_add=True)
	price = models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
	room = models.CharField(max_length=100,blank=True,null=True)
	message = models.TextField(max_length=500, blank=True, null=True)
	reply_message = models.TextField(max_length=500, blank=True, null=True)

	accepted_at = models.DateTimeField(blank=True,null=True)
	cancelled_at = models.DateTimeField(blank=True,null=True)
	requested = models.BooleanField(default=True)

	expert_pin = models.CharField(max_length=10)
	user_pin = models.CharField(max_length=10)
	expert_count = models.IntegerField()
	user_count = models.IntegerField()

	disconnected = models.DateTimeField(blank=True,null=True)

	time_started = models.DateTimeField(blank=True,null=True)
	time_ended = models.DateTimeField(blank=True,null=True)
	completed = models.BooleanField(default=False)

	paid_at = models.DateTimeField(blank=True,null=True)


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


	def __unicode__(self):
		return self.user.email
		

class Rating(models.Model):
	user = models.ForeignKey(User, related_name='rating_user')
	expert = models.ForeignKey(User, related_name='rating_expert')
	rating = models.IntegerField()
	comment = models.TextField()
	title = models.CharField(max_length=100)
	date = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.expert.email

class Message(models.Model):
	sender = models.ForeignKey(User, related_name='message_sender')
	reciever = models.ForeignKey(User, related_name='messege_reciever')
	message = models.TextField()
	title = models.CharField(max_length=100)
	sent_at = models.DateTimeField(auto_now_add=True)
	read_at = models.DateTimeField(null=True,blank=True)

	def new(self):
		"""returns whether the recipient has read the message or not"""
		if self.read_at is not None:
			return False
		return True

	def __unicode__(self):
		return self.title    


class ConferenceLine(models.Model):
	pin = models.CharField(max_length=10)  #change to 10
	talk = models.ForeignKey(Talk, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	expert = models.BooleanField(default=False)


	def __unicode__(self):
		return self.pin    


class CallIn(models.Model):
	twilio_call_key = models.CharField(max_length=100)
	talk = models.ForeignKey(Talk, blank=True, null=True)
	time_started = models.DateTimeField(auto_now_add=True)
	time_ended = models.DateTimeField(auto_now_add=True)
	expert = models.BooleanField(default=False)

	def __unicode__(self):
		return self.talk.user.email    


class Favorite(models.Model):
	user = models.ForeignKey(User, related_name='favorite_user')
	expert = models.ForeignKey(User, related_name='favorite_expert')
	created_at = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.user    



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
				'background' ,
				'expertise' ,
				'title',
				'time_zone',
				'price' ,
				'tags',
				'picture',
				'twitter',
				'linkedin',
				StrictButton('Submit', name='updateprofile', type='submit',css_class='btn-primary btn-lg'),
		)


class TalkForm(ModelForm):
	class Meta:
		model = Talk
		fields = ['time', 'message']

	def __init__(self, *args, **kwargs):
		super(TalkForm, self).__init__(*args, **kwargs)
		self.helper= FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_id = 'upload-form'
		self.helper.label_class = 'col-lg-3'
		self.helper.field_class = 'col-lg-9'
		self.helper.layout = Layout(
				'time',
				'message' ,
				StrictButton('Submit', name='requestform', type='submit',css_class='btn-primary btn-lg'),
		)

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

class MessageForm(ModelForm):
	class Meta:
		model = Message
		exclude = ['sender', 'reciever', 'sent_at', 'read_at']

	def __init__(self, *args, **kwargs):
		super(MessageForm, self).__init__(*args, **kwargs)
		self.helper= FormHelper()
		self.helper.form_class = 'form-horizontal'
		self.helper.form_id = 'upload-form'
		self.helper.label_class = 'col-lg-3'
		self.helper.field_class = 'col-lg-9'
		self.helper.layout = Layout(
				'title' ,
				'message' ,
				# StrictButton('Send', name='sendmessage', type='submit',css_class='btn-primary btn-lg'),
		)


# extended form for allauth
class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

