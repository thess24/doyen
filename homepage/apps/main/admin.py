from django.contrib import admin
from apps.main.models import ExpertProfile, Talk, Rating, Message, CallIn, Favorite, TalkTime, UserCard


class TalkAdmin(admin.ModelAdmin):
    list_display = ('user', 'expert', 'time', 'accepted','cancelled','requested','call_length')

class CallInAdmin(admin.ModelAdmin):
    list_display = ('talk','time_started', 'time_ended','expert')

admin.site.register(ExpertProfile)
admin.site.register(Talk, TalkAdmin)
admin.site.register(Rating)
admin.site.register(Message)
admin.site.register(TalkTime)
admin.site.register(Favorite)
admin.site.register(CallIn, CallInAdmin)
admin.site.register(UserCard)



########## TODO 

### Necessary

# finish up talkpayment view
# 4. finish email templates
	# add 'times' to accept, reject, reminder emails
	# do invoice email template
	# do payment email template
# 6. approve payments area for jon
	# make charges actually submit


# dont allow submitting empty request -- it still shows up in requests for expert
# make reply message work in message url area
# give errors when message fails to send (if not putting both fields)
# make message send via ajax
# favorite via ajax
# mark message as read once you click on it (ajax)
# give error for time request if times not filled out
# fix error if no card and try to go to checkout
# dont allow changing request (time) once submitted by accessing url
# dont allow changing card info once submitted by accessing url
# fix tagging
# make tagging page template
# make time select dropdown work better
# redo talk area to show dial in info
# have talks show up for expert to see what they have scheduled
# put stripe keys in settings and reference in views -- make env variables
# make frontpage
# redo footer
# make faq page
# make tos page
# make about us page
# make privacy policy page
# test sendat feature of emails
# test conference calls and make sure everything is properly logged
# check to see if conference is allowed at time, and if one is scheduled w pin



### Nice to have

# add text email template fallbacks
# status indicator for checkout process (how many steps left)
# social auth creds
# ability to send ajax messages from /messages
# check image size on upload
# alerts for form submits - bootstrap growl
