from django.contrib import admin
from apps.main.models import ExpertProfile, Talk, Rating, Message


class TalkAdmin(admin.ModelAdmin):
    list_display = ('user', 'expert', 'time', 'accepted','cancelled','requested')


admin.site.register(ExpertProfile)
admin.site.register(Talk, TalkAdmin)
admin.site.register(Rating)
admin.site.register(Message)



### DONE
# login/logout/pw
# privacy policy


### TODO

# 1. get time of call - process payments
# 2. accept cc info and check cards before charged




# add categories
# make favorites work
# submit 3 times at once
# click on tags to go to search page
# social auth creds
# accept payments--map this out
# model for stripe keys
# restrict reviews only if youve had call
# ability to send ajax messages from /messages
# ability to send ajax messages from expert page if logged in
# check image size on upload
# message count
# alerts for form submits - bootstrap growl
# check to see if conference is allowed at time, and if one is scheduled w pin
