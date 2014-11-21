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
# profile page for expert
# make twilio call work--first as standalone, then map out
# accept payments--map this out
# tos


### Needed
# github private
# aws account
# social auth signups--fb,twit,g+,lin
# twilio account
# stripe account
# mailgun/ mandrill account