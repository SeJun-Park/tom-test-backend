from django.urls import path
from . import views

urlpatterns = [
    path("", views.Teams.as_view()),
    path("search/", views.TeamSearch.as_view()),
    path("<int:pk>/", views.TeamDetail.as_view()),
    path("<int:pk>/players/", views.TeamPlayers.as_view()),
    path("<int:pk>/players/goalstats/", views.TeamPlayersGoalStats.as_view()),
    path("<int:pk>/players/tomstats/", views.TeamPlayersTOMStats.as_view()),
    path("<int:pk>/players/connected/", views.TeamPlayersConnected.as_view()),
    path("<int:pk>/players/notconnected/", views.TeamPlayersNotConnected.as_view()),
    path("<int:pk>/games/", views.TeamGames.as_view()),
    path("<int:pk>/games-relative/", views.TeamGamesRelative.as_view()),
    path("<int:pk>/goals/", views.TeamGoals.as_view()),
    path("<int:pk>/goals-relative/", views.TeamGoalsRelative.as_view()),
    path("<int:pk>/goals/against/", views.TeamGoalsAgainst.as_view()),
    path("<int:pk>/goals-relative/against/", views.TeamGoalsAgainstRelative.as_view()),
    path("<int:pk>/toms/", views.TeamToms.as_view()),
    path("<int:pk>/superplayers/", views.TeamSuperPlayers.as_view()),
    path("<int:pk>/vsteams/", views.TeamVSteams.as_view()),
    path("<int:pk>/stats/", views.TeamStats.as_view()),
    path("<int:pk>/stats-relative/", views.TeamStatsRelative.as_view()),
]