from django.urls import path
from . import views

urlpatterns = [
    path("", views.Teams.as_view()),
    path("search/", views.TeamSearch.as_view()),
    path("recently/", views.TeamsRecently.as_view()),
    path("<int:pk>/", views.TeamDetail.as_view()),
    path("<int:pk>/photo", views.TeamPhoto.as_view()),
    path("<int:pk>/readonly/", views.TeamDetailReadOnly.as_view()),
    path("<int:pk>/connecting-spvsrs/", views.TeamConnectingSpvsrs.as_view()),
    path("<int:pk>/spvsrs/", views.TeamSpvsrs.as_view()),
    path("<int:pk>/spvsrs/connecting/", views.TeamSpvsrsConnecting.as_view()),
    path("<int:pk>/spvsrs/connecting/cancel/", views.TeamSpvsrsConnectingCancel.as_view()),
    path("<int:pk>/spvsrs/connect/", views.TeamSpvsrsConnect.as_view()),
    path("<int:pk>/spvsrs/connect/cancel/", views.TeamSpvsrsConnectCancel.as_view()),
    path("<int:pk>/players/", views.TeamPlayers.as_view()),
    path("<int:pk>/players/goalstats/", views.TeamPlayersGoalStats.as_view()),
    path("<int:pk>/players/tomstats/", views.TeamPlayersTOMStats.as_view()),
    path("<int:pk>/players/connected/", views.TeamPlayersConnected.as_view()),
    path("<int:pk>/players/notconnected/", views.TeamPlayersNotConnected.as_view()),
    path("<int:pk>/players/connecting/", views.TeamPlayersConnecting.as_view()),
    path("<int:pk>/games/", views.TeamGames.as_view()),
    path("<int:pk>/games-relative/", views.TeamGamesRelative.as_view()),
    path("<int:pk>/goals/", views.TeamGoals.as_view()),
    path("<int:pk>/goals-relative/", views.TeamGoalsRelative.as_view()),
    path("<int:pk>/goals/against/", views.TeamGoalsAgainst.as_view()),
    path("<int:pk>/goals-relative/against/", views.TeamGoalsAgainstRelative.as_view()),
    path("<int:pk>/toms/", views.TeamToms.as_view()),
    path("<int:pk>/tomvoteing/", views.TeamTomVoteIng.as_view()),
    path("<int:pk>/superplayers/", views.TeamSuperPlayers.as_view()),
    path("<int:pk>/vsteams/", views.TeamVSteams.as_view()),
    path("<int:pk>/stats/", views.TeamStats.as_view()),
    path("<int:pk>/stats-relative/", views.TeamStatsRelative.as_view()),
    path("<int:pk>/votes/", views.TeamVotes.as_view()),
    path("<int:pk>/feeds/", views.TeamFeeds.as_view()),
    path("<int:pk>/feeds/<int:feed_pk>/", views.TeamFeedDetail.as_view()),
    path("<int:pk>/feeds/<int:feed_pk>/photos/", views.TeamFeedPhotos.as_view()),
    path("<int:pk>/notis/month/", views.TeamNotisMonth.as_view()),
    path("<int:pk>/notis/bymonth/", views.TeamNotisByMonth.as_view()),
    path("<int:pk>/schedules/", views.TeamSchedules.as_view()),
    path("<int:pk>/schedules/<int:schedule_pk>/", views.TeamScheduleDetail.as_view()),
    path("<int:pk>/schedules/month/", views.TeamSchedulesMonth.as_view()),
    path("<int:pk>/schedules/bymonth/", views.TeamSchedulesByMonth.as_view()),
    path("<int:pk>/dues/details/", views.TeamDuesDetail.as_view()),
    path("<int:pk>/dues/details/<int:detail_pk>/", views.TeamDuesDetailDetail.as_view()),
    path("<int:pk>/dues/details/in/<int:item_pk>/", views.TeamDuesInItemDetail.as_view()),
    path("<int:pk>/dues/details/out/<int:item_pk>/", views.TeamDuesOutItemDetail.as_view()),
    path("<int:pk>/dues/details/<int:detail_pk>/in/items/", views.TeamDuesInItems.as_view()),
    path("<int:pk>/dues/details/<int:detail_pk>/out/items/", views.TeamDuesOutItems.as_view()),
    path("<int:pk>/dues/details/<int:detail_pk>/in/amount/", views.TeamDuesInAmount.as_view()),
    path("<int:pk>/dues/details/<int:detail_pk>/out/amount/", views.TeamDuesOutAmount.as_view()),
    path("<int:pk>/dues/payments/", views.TeamDuesPayment.as_view()),
    path("<int:pk>/dues/payments/items/<int:item_pk>/", views.TeamDuesPaymentItemDetail.as_view()),
    path("<int:pk>/dues/payments/<int:payment_pk>/", views.TeamDuesPaymentDetail.as_view()),
    path("<int:pk>/dues/payments/<int:payment_pk>/items/", views.TeamDuesPaymentItems.as_view()),
    path("<int:pk>/dues/payments/<int:payment_pk>/items/readonly/", views.TeamDuesPaymentItemsReadOnly.as_view()),
    path("<int:pk>/dues/payments/<int:payment_pk>/items/extra/", views.TeamDuesPaymentItemsExtra.as_view()),
    path("<int:pk>/dues/details/list/", views.TeamDuesDetailList.as_view()),
    path("<int:pk>/dues/payments/list/", views.TeamDuesPaymentList.as_view()),
]