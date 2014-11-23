from django.contrib import admin
from apps.main.models import ExpertProfile, Talk, RequestedTalk, Rating, Message


admin.site.register(ExpertProfile)
admin.site.register(Talk)
admin.site.register(RequestedTalk)
admin.site.register(Rating)
admin.site.register(Message)



### DONE
# login/logout/pw
# privacy policy


### TODO

# 1. ability to make req talks into real talks --accept/decline message, email, and model submit
# 2. form submit to request times to talk
# 3. conference line setup, scheduling
# 4. get time of call - process payments
# 5. accept cc info and check cards before charged




# login emails
# social auth creds
# make twilio call work--first as standalone, then map out
# accept payments--map this out
# tos
# model for stripe keys



# form for user to request talk on expert profile page
# make acceptance/decline work
# make comment/rating system work
# limit rating from 1 to 5
# restrict reviews only if youve had call
# ability to send ajax messages from /messages
# ability to send ajax messages from expert page if logged in


# check image size on upload
# form for expert to enter full name
# message count
# alerts for form submits - jelly popup


### Needed
# github private
# aws account
# social auth signups--fb,twit,g+,lin
# twilio account
# stripe account
# mailgun/ mandrill account