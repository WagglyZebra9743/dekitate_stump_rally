from .models import AllLog

def register_info_log(name,message):
    AllLog.objects.create(
        name=name,
        message=message,
        type='info'
    )