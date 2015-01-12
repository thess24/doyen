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


 
########## TODO 

### Necessary
# 2. expert page html
# faq page html
# about us html
# 5. call window
# 8. make sure pins generated properly-- check times


# make sure conf call is working
	# check to see if conference is allowed at time, and if one is scheduled w pin

# check image size on upload, resize for smaller pics
# dont allow changing card info once submitted by accessing url



######### Nice to have
# make disconnected button do something
# add text email template fallbacks
# social auth creds
# alerts for form submits - bootstrap growl



########## known bugs
# fix dollar sign in expert page - not showing up properly in production
# dont allow accepting "accept time" without selecting a time
# make sure user gets stripe id when submitting card for first time
# error handling/alerts for payment not going through