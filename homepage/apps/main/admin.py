from django.contrib import admin
from apps.main.models import ExpertProfile, Talk, Rating, CallIn, Favorite, TalkTime, UserCard, UserProfile


class TalkAdmin(admin.ModelAdmin):
    list_display = ('user', 'expert', 'time', 'accepted','cancelled','requested','call_length')

class CallInAdmin(admin.ModelAdmin):
    list_display = ('talk','time_started', 'time_ended','expert')

admin.site.register(ExpertProfile)
admin.site.register(Talk, TalkAdmin)
admin.site.register(Rating)
admin.site.register(TalkTime)
admin.site.register(Favorite)
admin.site.register(CallIn, CallInAdmin)
admin.site.register(UserCard)
admin.site.register(UserProfile)


 
################ TODO 

####### Necessary
# explaination text for forms
	# applying for expert

# make pics uniform size in frontend
# default image if expert deletes the one they have


########## known bugs
# make sure user gets stripe id when submitting card for first time
# error handling/alerts for payment not going through





######### Nice to have
# make disconnected button do something
# social auth creds
# alerts for form submits - bootstrap growl
# resize uploaded images







# Stripe paid account
# Github paid account
# Heroku paid account
# HTTPS purchase
# HTTPS online
# Twilio paid account


