from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>/", views.GameDetail.as_view()),
    path("<int:pk>/vote/", views.GameVote.as_view()),
    path("<int:pk>/vote/ballot/", views.GameVoteBallot.as_view()),
]