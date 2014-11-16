from django.contrib import admin
from apps.main.models import ExpertProfile, Talk, RequestedTalk 


admin.site.register(ExpertProfile)
admin.site.register(Talk)
admin.site.register(RequestedTalk)
