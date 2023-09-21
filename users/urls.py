from django.urls import path
from . import views

urlpatterns = [
    path("me/", views.Me.as_view()),
    path("logout/", views.LogOut.as_view()),
    path("isplayer/", views.IsPlayer.as_view()),
    path("isplayer/kakaologin/", views.KakaoLogIn.as_view()),
    path("isplayer/teams/", views.IsPlayerTeams.as_view()),
    path("isplayer/games/", views.IsPlayerGames.as_view()),
    path("isplayer/goalgames/", views.IsPlayerGoalGames.as_view()),
    path("isplayer/goals/", views.IsPlayerGoals.as_view()),
    path("isplayer/toms/", views.IsPlayerToms.as_view()),
    path("isplayer/superplayers/", views.IsPlayerSuperPlayers.as_view()),
    path("isspvsr/", views.IsSpvsr.as_view()),
    path("isspvsr/teams/", views.IsSpvsrTeams.as_view()),
    path("isspvsr/games/", views.IsSpvsrGames.as_view()),
    path("isspvsr/goals/", views.IsSpvsrGoals.as_view()),
    path("isspvsr/toms/", views.IsSpvsrToms.as_view()),
    path("isspvsr/superplayers/", views.IsSpvsrSuperPlayers.as_view()),
]