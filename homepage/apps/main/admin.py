from django.contrib import admin
from apps.main.models import ExpertProfile, Talk, RequestedTalk 


admin.site.register(ExpertProfile)
admin.site.register(Talk)
admin.site.register(RequestedTalk)



### DONE
# login/logout/pw
# privacy policy


### TODO
# login emails
# social auth creds
# page to list experts
# make twilio call work--first as standalone, then map out
# accept payments--map this out
# tos


# finish messaging
# form for user to request talk
# make acceptance/decline work
# real data in /talks
# make comment/rating system page for user to input data


### Needed
# github private
# aws account
# social auth signups--fb,twit,g+,lin
# twilio account
# stripe account
# mailgun/ mandrill account