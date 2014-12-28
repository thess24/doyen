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
	# test conference calls and make sure everything is properly logged
	# check to see if conference is allowed at time, and if one is scheduled w pin
	# change call routing to 6 digits-make sure zero shows up
# show errors on form submits
	# dont allow submitting empty request -- it still shows up in requests for expert
	# give error for time request if times not filled out
	# fix error if no card and try to go to checkout
# 4. finish email templates
	# add 'times' to accept, reject, reminder emails
	# do invoice email template
	# do payment email template
# 6. approve payments area for jon
	# make charges actually submit


# have talks show up for expert to see what they have scheduled
# put stripe keys in settings and reference in views -- make env variables
# test sendat feature of emails
# make rating expert work
# make hourly rate instead of minute rate



# redo footer
# make faq page
# make tos page
# make privacy policy page
# dont allow changing request (time) once submitted by accessing url
# dont allow changing card info once submitted by accessing url



### Nice to have

# favorite via ajax
# add text email template fallbacks
# status indicator for checkout process (how many steps left)
# social auth creds
# check image size on upload
# alerts for form submits - bootstrap growl
