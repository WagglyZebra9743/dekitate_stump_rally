from django.urls import path
 
from . import views
 
urlpatterns = [
    path("", views.index, name="index"),
    path("rules/",views.rules,name="rules"),
    path("play/",views.play,name="play"),
    path("stamp_add/",views.stamp_add_view,name="stamp_add_view"),
    path("stamp_success/<int:pk>/", views.stamp_success_view, name="stamp_success"),
    path("stamp_list",views.stamp_list,name="stamp_list"),
    path("player_info",views.player_info,name="player_info"),
]