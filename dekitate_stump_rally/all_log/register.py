from .models import AllLog

def register_info_log(name,message,player="",search_assist=""):
    AllLog.objects.create(
        name=name,
        message=message,
        type='info',
        player=player,
        search_assist=search_assist
    )

def register_create_log(name,message,player="",search_assist=""):
    AllLog.objects.create(
        name=name,
        message=message,
        type='create',
        player=player,
        search_assist=search_assist
    )

def register_error_log(name,message,player="",search_assist=""):
    AllLog.objects.create(
        name=name,
        message=message,
        type='error',
        player=player,
        search_assist=search_assist
    )

def register_warn_log(name,message,player="",search_assist=""):
    AllLog.objects.create(
        name=name,
        message=message,
        type='warn',
        player=player,
        search_assist=search_assist
    )