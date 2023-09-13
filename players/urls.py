from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>/", views.PlayerDetail.as_view()),
    path("<int:pk>/photo/", views.PlayerPhoto.as_view()),
    path("<int:pk>/connecting/", views.PlayerConnecting.as_view()),
    path("<int:pk>/connecting-cancel/", views.PlayerConnectingCancel.as_view()),
    path("<int:pk>/connect/", views.PlayerConnect.as_view()),
    path("<int:pk>/games/", views.PlayerGames.as_view()),
    path("<int:pk>/goalgames/", views.PlayerGoalGames.as_view()),
    path("<int:pk>/goals/", views.PlayerGoals.as_view()),
    path("<int:pk>/toms/", views.PlayerTOMS.as_view()),
    path("<int:pk>/superplayers/", views.PlayerSuperPlayers.as_view()),
    path("<int:pk>/superplayers/check", views.PlayerSuperplayerCheck.as_view()),
]