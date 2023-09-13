from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>/", views.GameDetail.as_view()),
    path("<int:pk>/players/", views.GameDailyPlayers.as_view()),
    path("<int:pk>/quotas/", views.GameQuotas.as_view()),
    path("<int:pk>/quotas/<int:quota_pk>/", views.GameQuotaDetail.as_view()),
    path("<int:pk>/vote/", views.GameVote.as_view()),
    path("<int:pk>/videos/", views.GameVideos.as_view()),
    path("<int:pk>/photos/", views.GamePhotos.as_view()),
]