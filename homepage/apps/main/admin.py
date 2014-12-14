from django.contrib import admin
from apps.main.models import ExpertProfile, Talk, Rating, Message, CallIn, Favorite


class TalkAdmin(admin.ModelAdmin):
    list_display = ('user', 'expert', 'time', 'accepted','cancelled','requested','call_length')

class CallInAdmin(admin.ModelAdmin):
    list_display = ('talk','time_started', 'time_ended','expert')

admin.site.register(ExpertProfile)
admin.site.register(Talk, TalkAdmin)
admin.site.register(Rating)
admin.site.register(Message)
admin.site.register(Favorite)
admin.site.register(CallIn, CallInAdmin)



### DONE
# login/logout/pw
# privacy policy


### TODO 




# do invoice email tempate
# do payment email template
# make email out into function -- more concise
# finish templates for emails
# add .txt files for emails
# dont allow changing request once submitted by accessing url
# add categories
# submit 3 times at once
# fix tagging
# social auth creds
# restrict reviews only if youve had call
# ability to send ajax messages from /messages
# ability to send ajax messages from expert page if logged in
# check image size on upload
# alerts for form submits - bootstrap growl
# check to see if conference is allowed at time, and if one is scheduled w pin
# change datetime.now() to timezone.now() from django utils -lookup in docs
