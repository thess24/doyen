from django.contrib import admin
from apps.main.models import ExpertProfile, Talk, Rating, CallIn, Favorite, TalkTime, UserCard


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



########## TODO 

### Necessary


# 2. expert page html
# 5. call window
# 6. approve payments works
# 8. make sure pins generated properly-- check times


 

# make sure conf call is working
	# check to see if conference is allowed at time, and if one is scheduled w pin
# 6. approve payments area for jon
	# make charges actually submit

# make disconnected button do something


# check image size on upload, resize for smaller pics


# front page

# dont allow changing request (time) once submitted by accessing url
# dont allow changing card info once submitted by accessing url




### Nice to have

# add text email template fallbacks
# social auth creds
# alerts for form submits - bootstrap growl



########## known bugs
# fix dollar sign in expert page - not showing up properly in production
