from apps.main.models import Message


def message_count(request):
    if request.user.is_authenticated():
    	count =  Message.objects.filter(reciever=request.user, read_at__isnull=True).count()
        return {'message_count': count}
    else:
        return {}