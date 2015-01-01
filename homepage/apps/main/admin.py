from django.contrib import admin
from apps.main.models import ExpertProfile, Talk, Rating, CallIn, Favorite, TalkTime, UserCard


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



########## TODO 

### Necessary

# make sure conf call is working
	# check to see if conference is allowed at time, and if one is scheduled w pin
# 4. finish email templates
	# make sure correct data is passed in
# 6. approve payments area for jon
	# make charges actually submit

# make tags area html work
# make disconnected button do something


#  2 finish email templates
#  3 call time window


# put stripe keys in settings and reference in views -- make env variables
# make hourly rate instead of minute rate
# stripe connect
# check image size on upload, resize for smaller pics


# requests page html
# front page
# redo footer
# make faq page
# make tos page
# make privacy policy page
# dont allow changing request (time) once submitted by accessing url
# dont allow changing card info once submitted by accessing url




### Nice to have

# favorite via ajax
# add text email template fallbacks
# social auth creds
# alerts for form submits - bootstrap growl


## finished templates (besides what is passed in-- so just layout)
# expertacceptnotify
# expertreminder
# useracceptnotify
# userreminder
# expertrequestnotify
# userrequestnotif
# userrejectnotify
# userrateexpert
# userinvoice


