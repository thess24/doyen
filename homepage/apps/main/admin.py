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



# dont allow submitting empty request
# make reply message work
# dont allow changing request once submitted by accessing url
# add categories
# fix tagging
# make tagging page template
# check to see if conference is allowed at time, and if one is scheduled w pin




### Nice to have

# add text email template fallbacks
# make time select dropdown work better
# status indicator for checkout process (how many steps left)
# social auth creds
# ability to send ajax messages from /messages
# ability to send ajax messages from expert page if logged in
# check image size on upload
# alerts for form submits - bootstrap growl
