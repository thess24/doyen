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


class ExpertProfile(models.Model):
	user = models.OneToOneField(User)
	# credentials = models.TextField()  #split btwn background/areas of expertise
	background = models.TextField()  #split btwn background/areas of expertise
	expertise = models.TextField()  #split btwn background/areas of expertise
	price = models.DecimalField(max_digits=6, decimal_places=2)
	picture = models.ImageField(upload_to='profilepics')
	online = models.BooleanField(default=False)

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
	pin = models.CharField(max_length=10,blank=True,null=True)  # pin for call
	message = models.TextField(max_length=500, blank=True, null=True)
	reply_message = models.TextField(max_length=500, blank=True, null=True)
	accepted = models.BooleanField(default=False)
	accepted_at = models.DateTimeField(blank=True,null=True)
	cancelled = models.BooleanField(default=False)
	cancelled_at = models.DateTimeField(blank=True,null=True)
	requested = models.BooleanField(default=True)

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
	pin = models.CharField(max_length=5)
	talk = models.ForeignKey(Talk, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.pin    


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
				'price' ,
				'tags',
				'picture' ,
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



# class ProductForm(ModelForm):
# 	description = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 15}))

# 	class Meta:
# 		model = Product
# 		exclude = ['purchases', 'user_created', 'active', 'new', 'popular', 'featured']

# 	def clean(self):
# 		cleaned_data = super(ProductForm, self).clean()
# 		image = cleaned_data.get('image',False)
# 		product_file = cleaned_data.get('product_file',False)
# 		product_name = cleaned_data.get('name',False)

# 		pname = Product.objects.filter(name=product_name)
# 		if pname:
# 			raise ValidationError("That name already exists")

# 		if image: 
# 			if image._size > MAX_IMG_SIZE:
# 				raise ValidationError("Image too large - must be less than 300kb")

# 			imgtype = image.name.split(".")[-1]
# 			if imgtype not in ALLOWED_IMG_TYPES:
# 				raise ValidationError("Must by a jpg, jpeg, gif, or png")

# 		if product_file:
# 			filetype = product_file.name.split(".")[-1]
# 			if filetype not in ALLOWED_FILE_TYPES:
# 				raise ValidationError("Must by a ppt, potx, or pptx")

# 			if product_file._size > MAX_FILE_SIZE:
# 				raise ValidationError("File too large - must be less than 4mb")

# 		return cleaned_data

	# def __init__(self, *args, **kwargs):
	# 	super(ProductForm, self).__init__(*args, **kwargs)
	# 	self.helper= FormHelper()
	# 	self.helper.form_class = 'form-horizontal'
	# 	self.helper.form_id = 'upload-form'
	# 	self.helper.label_class = 'col-lg-3'
	# 	self.helper.field_class = 'col-lg-9'
	# 	self.helper.layout = Layout(
	# 			'name' ,
	# 			'description' ,
	# 			PrependedText('price', '$'),
	# 			'product_file' ,
	# 			'image' ,
	# 			'category' ,
	# 			'pages' ,
	# 			'tags' ,
	# 			StrictButton('Continue >', name='addproduct', type='submit',css_class='btn-primary btn-lg'),
	# 	)







# 3 times to ask expert about -- request for talk
# user extension to store stripe creds
