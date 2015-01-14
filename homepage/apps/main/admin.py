from django.contrib import admin
from apps.main.models import ExpertProfile, Talk, Rating, CallIn, Favorite, TalkTime, UserCard, UserProfile


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
admin.site.register(UserProfile)


 
########## TODO 

### Necessary
# 2. expert page html
# explaination text for forms
	# applying for expert

# make so value isnt require for me to reject -- make 2 seperate forms?
# check image size on upload, resize for smaller pics
# make pics uniform size 
# dont allow changing card info once submitted by accessing url



######### Nice to have
# make disconnected button do something
# social auth creds
# alerts for form submits - bootstrap growl



########## known bugs
# fix dollar sign in expert page - not showing up properly in production
# make sure user gets stripe id when submitting card for first time
# error handling/alerts for payment not going through