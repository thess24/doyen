from django.contrib import admin
from apps.main.models import ExpertProfile, Talk, Rating, CallIn, Favorite, TalkTime, UserCard, UserProfile
from sorl.thumbnail.admin import AdminImageMixin


class TalkAdmin(admin.ModelAdmin):
    list_display = ('user', 'expert', 'time', 'accepted','cancelled','requested','call_length')

class CallInAdmin(admin.ModelAdmin):
    list_display = ('talk','time_started', 'time_ended','expert')

class ExpertProfileAdmin(AdminImageMixin, admin.ModelAdmin):
    pass

admin.site.register(ExpertProfile, ExpertProfileAdmin)
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

# verify card is valid



# html in review page to include more info
# frontend form validation/flow for talkpayment addcard
# talkpayment html -- move addcard
# limit talks to 1 month away max, make sure request is for a time in future
# add correct tags to expertprofile
# make all in better spot
# make searching area distinct from dashboard areas
# html for dropdown areas
# html for tagging area/category
# hsts 


########## known bugs
# error handling/alerts for payment not going through





######### Nice to have
# make disconnected button do something
# social auth creds
# alerts for form submits - bootstrap growl




# transfer domain
# Stripe paid account
# Github paid account
# Heroku paid account
# ssl cert purchase
# Twilio paid account


