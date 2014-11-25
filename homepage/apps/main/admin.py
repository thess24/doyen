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


# 3. conference line setup, scheduling
# 4. get time of call - process payments
# 5. accept cc info and check cards before charged




# social auth creds
# make twilio call work--first as standalone, then map out
# accept payments--map this out
# model for stripe keys
# restrict reviews only if youve had call
# ability to send ajax messages from /messages
# ability to send ajax messages from expert page if logged in
# check image size on upload
# message count
# alerts for form submits - bootstrap growl

