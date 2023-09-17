import time
from django.db.models.functions import TruncMonth, TruncYear
from django.db.models import Count, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, F
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from rest_framework import status
from .models import Team, TeamFeed, TeamNoti, TeamSchedule, DuesDetail, DuesPayment, DuesPaymentItem, DuesInItem, DuesOutItem
from players.models import Player
from games.models import Game, GoalPlayer, Vote
from .serializers import TeamSerializer, TinyTeamSerializer, UploadTeamSerializer, UploadTeamFeedSerializer, TeamFeedSerializer, TeamNotiSerializer, TeamScheduleSerializer, TeamVoteSerializer, DuesDetailSerializer, DuesPaymentSerializer, DuesInItemSerializer, DuesOutItemSerializer, DuesPaymentItemSerializer, UploadDuesPaymentItemSerializer
from players.serializers import TinyPlayerSerializer, PlayerSerializer, UploadPlayerSerializer
from games.serializers import TinyGameSerializer, UploadGameSerializer
from medias.serializers import PhotoSerializer
from superplayers.serializers import SuperPlayerSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# Create your views here.

class Teams(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UploadTeamSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            team = serializer.save(spvsr=user)
            serializer = UploadTeamSerializer(team, context={"request" : request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeamDetail(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound        

    def get(self, request, pk):
        team = self.get_object(pk)
        serializer = TeamSerializer(team, context={"request" : request})
        return Response(serializer.data)

    def put(self, request, pk):
        pass

class TeamSearch(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        search_name = request.data.get("name")
        search_result = Team.objects.filter(name__icontains=search_name)
        search_result_sorted = search_result.order_by("name")
        serializer = TinyTeamSerializer(search_result_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeamPlayers(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_players_all = team.players.all()
        team_players_all_sorted = team_players_all.order_by("backnumber")
        serializer = TinyPlayerSerializer(team_players_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        try:
            team = self.get_object(pk)

            if team.spvsr != request.user:
                raise PermissionDenied

            data = request.data.copy()
            # data['team'] = team.id

            serializer = UploadPlayerSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    player = serializer.save(team=team)
                    serializer = UploadPlayerSerializer(player)
            # player_name = request.data.get("name")
            # player_backnumber = request.data.get("backnumber")
            # player_description = request.data.get("description", None)

            # player = Player.objects.create(
            #     team=team,
            #     name=player_name,
            #     backnumber=player_backnumber,
            #     description=player_description
            # )

            # player.save()
            else:
                print(serializer.errors)
                print("here!")

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TeamPlayersGoalStats(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_players_all = team.players.all()
        team_players_all_sorted_by_goals = team_players_all.annotate(goal_count=Count('goals')).order_by('-goal_count')
        serializer = TinyPlayerSerializer(team_players_all_sorted_by_goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamPlayersTOMStats(APIView):
        
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_players_all = team.players.all()
        team_players_all_sorted_by_tom_games = team_players_all.annotate(tom_games_count=Count('tom_games')).order_by('-tom_games_count')
        serializer = TinyPlayerSerializer(team_players_all_sorted_by_tom_games, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamPlayersConnected(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_players_all = team.players.all()
        team_players_connected = team_players_all.filter(connected_user__isnull=False)
        team_players_connected_sorted = team_players_connected.order_by("name")
        serializer = TinyPlayerSerializer(team_players_connected_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeamPlayersNotConnected(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_players_all = team.players.all()
        team_players_not_connected = team_players_all.filter(connected_user__isnull=True, connecting_user__isnull=True)
        team_players_not_connected_sorted = team_players_not_connected.order_by("backnumber")
        serializer = TinyPlayerSerializer(team_players_not_connected_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeamPlayersConnecting(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_players_all = team.players.all()
        team_players_connecting = team_players_all.filter(connecting_user__isnull=False)
        team_players_connecting_sorted = team_players_connecting.order_by("name")
        serializer = TinyPlayerSerializer(team_players_connecting_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeamGames(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_games_all = team.games.all()
        team_games_all_sorted = team_games_all.order_by("-date")
        serializer = TinyGameSerializer(team_games_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):

        team = self.get_object(pk)

        if team.spvsr != request.user:
            raise PermissionDenied 

        serializer = UploadGameSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    game = serializer.save(team=team)

                    participants = request.data.get("participants")
                    if participants:
                        game.participants.clear()
                        for participant_pk in participants:
                            participant = Player.objects.get(pk=participant_pk)
                            game.participants.add(participant)
                        
                    game_datetime = timezone.datetime.combine(game.date, game.end_time)
                    vote_start = game_datetime
                    vote_end = game_datetime + timedelta(days=2)
                    vote_end = vote_end.replace(hour=0, minute=0, second=0)

                    vote_start = timezone.make_aware(vote_start)
                    vote_end = timezone.make_aware(vote_end)

                    # vote 객체 생성
                    vote = Vote.objects.create(
                        game=game,
                        start=vote_start,
                        end=vote_end
                    )

                    vote.candidates.set(game.participants.all())

                    TeamNoti.objects.create(
                        team=team,
                        game=game,
                        dateTime=game.created_at,
                        name="Tom",
                        description="삼오엠 매니저",
                        title=f"VS {game.vsteam}",
                        category="game",
                        payload="새로운 경기가 등록되었습니다.",
                    )

                    TeamNoti.objects.create(
                        team=team,
                        game=game,
                        dateTime=vote_start,
                        name="Tom",
                        description="삼오엠 매니저",
                        title=f"VS {game.vsteam}",
                        category="tom",
                        payload="3OM 투표가 시작되었습니다.",
                    )

                    TeamSchedule.objects.create(
                        team=team,
                        game=game,
                        dateTime=game_datetime,
                        category="game",
                        title=f"VS {game.vsteam}"
                    )


                    serializer = UploadGameSerializer(game)

                    return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e: 
                # 어떤 에러가 나든지 라는 뜻.
                print(e)
                raise ParseError
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeamGamesRelative(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        team = self.get_object(pk)
        vsteam = request.data.get("vsteam")
        team_games_all = team.games.all()
        team_games_relative = team_games_all.filter(vsteam=vsteam)
        team_games_relative_sorted = team_games_relative.order_by("-date")
        serializer = TinyGameSerializer(team_games_relative_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class TeamGoalGames(APIView):

#     permission_classes = [IsAuthenticated]

#     def get_object(self, pk):
#         try:
#             team = Team.objects.get(pk=pk)
#             return team
#         except Team.DoesNotExist:
#             raise NotFound

#     def get(self, request, pk):
#         team = self.get_object(pk)
#         team_players_all = team.players.all()
#         player_goal_games_all = Game.objects.filter(goals__player__in=team_players_all)
#         player_goal_games_all_sorted = player_goal_games_all.order_by("-date")
#         serializer = TinyGameSerializer(player_goal_games_all_sorted, many=True)
#         return Response(serializer.data)
    

class TeamGoals(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            team = self.get_object(pk)
            team_games_all = team.games.all()
            # team_goals_all = GoalPlayer.objects.filter(game__in=team_games_all).count()

            team_goals_all = 0
            for game in team_games_all:
                if game.team_score:
                    team_goals_all = team_goals_all + game.team_score

            response_data = {
                "goals" : team_goals_all
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TeamGoalsRelative(APIView):
        
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        try:
            team = self.get_object(pk)
            vsteam = request.data.get("vsteam")

            team_games_all = team.games.all()
            team_games_relative = team_games_all.filter(vsteam=vsteam)
            # team_goals_relative_all = GoalPlayer.objects.filter(game__in=team_games_relative).count()

            team_goals_relative_all = 0
            for game in team_games_relative:
                if game.team_score:
                    team_goals_relative_all = team_goals_relative_all + game.team_score

            response_data = {
                "goals" : team_goals_relative_all
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TeamGoalsAgainst(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            team = self.get_object(pk)
            team_games_all = team.games.all()
            # team_goals_all = GoalPlayer.objects.filter(game__in=team_games_all).count()

            team_goals_against_all = 0
            for game in team_games_all:
                if game.vsteam_score:
                    team_goals_against_all = team_goals_against_all + game.vsteam_score

            response_data = {
                "goals" : team_goals_against_all
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TeamGoalsAgainstRelative(APIView):
        
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        try:
            team = self.get_object(pk)
            vsteam = request.data.get("vsteam")

            team_games_all = team.games.all()
            team_games_relative = team_games_all.filter(vsteam=vsteam)
            # team_goals_relative_all = GoalPlayer.objects.filter(game__in=team_games_relative).count()

            team_goals_against_relative_all = 0
            for game in team_games_relative:
                if game.vsteam_score:
                    team_goals_against_relative_all = team_goals_against_relative_all + game.vsteam_score

            response_data = {
                "goals" : team_goals_against_relative_all
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TeamSuperPlayers(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_superplayers_all = team.superplayers.all()
        team_superplayers_all_sorted = team_superplayers_all.order_by("-created_at")
        serializer = SuperPlayerSerializer(team_superplayers_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeamVSteams(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_games_all = team.games.all()

        vsteams_set = set()

        for game in team_games_all:
            vsteams_set.add(game.vsteam)

        vsteams = list(vsteams_set)

        response_data = {
            "vsteams" : vsteams,
        }

        return Response(response_data, status=status.HTTP_200_OK)

class TeamStats(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            team = self.get_object(pk)
            team_games_all = team.games.all()

            team_not_recorded_games_all = team_games_all.filter(Q(team_score__isnull=True) | Q(vsteam_score__isnull=True))
            team_win_games_all = team_games_all.filter(team_score__gt=F('vsteam_score'))
            team_draw_games_all = team_games_all.filter(team_score=F('vsteam_score'))
            team_lose_games_all = team_games_all.filter(team_score__lt=F('vsteam_score'))

            not_recorded_count_all = team_not_recorded_games_all.count()
            win_count_all = team_win_games_all.count()
            draw_count_all = team_draw_games_all.count()
            lose_count_all = team_lose_games_all.count()

            response_data = {
                "not" : not_recorded_count_all,
                "win" : win_count_all,
                "draw" : draw_count_all,
                "lose" : lose_count_all,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TeamStatsRelative(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        try:
            team = self.get_object(pk)
            vsteam = request.data.get("vsteam")
            team_games_all = team.games.all()
            team_games_vsteam_all = team_games_all.filter(vsteam=vsteam)

            team_not_recorded_games_relative = team_games_vsteam_all.filter(Q(team_score__isnull=True) | Q(vsteam_score__isnull=True))
            team_win_games_relative = team_games_vsteam_all.filter(team_score__gt=F('vsteam_score'))
            team_draw_games_relative = team_games_vsteam_all.filter(team_score=F('vsteam_score'))
            team_lose_games_relative = team_games_vsteam_all.filter(team_score__lt=F('vsteam_score'))

            not_recorded_count_relative = team_not_recorded_games_relative.count()
            win_count_relative = team_win_games_relative.count()
            draw_count_relative = team_draw_games_relative.count()
            lose_count_relative = team_lose_games_relative.count()

            response_data = {
                "vsteam" : vsteam,
                "not" : not_recorded_count_relative,
                "win" : win_count_relative,
                "draw" : draw_count_relative,
                "lose" : lose_count_relative,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TeamTomVoteIng(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        now = timezone.now()

        team_toms_all = team.games.all().annotate(
            vote_start=F('vote__start'),
            vote_end=F('vote__end')
        ).filter(
            Q(vote_start__lte=now) & Q(vote_end__gte=now)
        ).distinct()

        team_toms_all_sorted = team_toms_all.order_by("-date")
        serializer = TinyGameSerializer(team_toms_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeamToms(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        now = timezone.now()

        team_games_all = team.games.all()
        team_toms_all = team_games_all.filter(toms__isnull=False, vote__end__lt=now).distinct()
        team_toms_all_sorted = team_toms_all.order_by("-date")
        serializer = TinyGameSerializer(team_toms_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeamVotes(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_votes_all = team.tvotes.all()
        team_votes_all_sorted = team_votes_all.order_by("-start")
        serializer = TeamVoteSerializer(team_votes_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeamFeeds(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_feeds_all = team.feeds.all()
        team_feeds_all_sorted = team_feeds_all.order_by("-created_at")
        serializer = TeamFeedSerializer(team_feeds_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        try:
            team = self.get_object(pk)

            if team.spvsr != request.user:
                raise PermissionDenied

            data = request.data.copy()
            data['team'] = team.id

            serializer = UploadTeamFeedSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    feed = serializer.save()
                    serializer = UploadTeamFeedSerializer(feed)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
                

class TeamFeedDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            feed = TeamFeed.objects.get(pk=pk)
            return feed
        except TeamFeed.DoesNotExist:
            raise NotFound

    def get(self, request, pk, feed_pk):
        try:
            feed = self.get_object(feed_pk)
            serializer = TeamFeedSerializer(feed)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, feed_pk):
        try:
            feed = self.get_object(feed_pk)
            serializer = TeamFeedSerializer(feed, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, feed_pk):
        feed = self.get_object(feed_pk)
        team = feed.team

        if team.spvsr != request.user:
            raise PermissionDenied

        feed.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class TeamFeedPhotos(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            feed = TeamFeed.objects.get(pk=pk)
            return feed
        except TeamFeed.DoesNotExist:
            raise NotFound
    
    def post(self, request, pk, feed_pk):
        feed = self.get_object(pk=feed_pk)
        team = feed.team

        if request.user != team.spvsr:
            raise PermissionDenied

        serializer = PhotoSerializer(data=request.data)

        if serializer.is_valid():
            photo = serializer.save(team=team, feed=feed)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamNotisMonth(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)

        # 년월로 그룹화
        dates = team.notis.annotate(month_created=TruncMonth('dateTime')).values('month_created').distinct().order_by('-month_created')

        # 결과를 'YYYY년 MM월' 형식으로 변환
        formatted_dates = [date['month_created'].strftime('%Y년 %m월') for date in dates]

        return Response(formatted_dates, status=status.HTTP_200_OK)


class TeamNotisByMonth(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        team = self.get_object(pk)
        year = request.data.get("year")
        month = request.data.get("month")

        team_notis_all = team.notis.all()
        team_notis_by_month = team_notis_all.filter(dateTime__year=year, dateTime__month=month)
        team_notis_by_month_sorted = team_notis_by_month.order_by("-dateTime")
        serializer = TeamNotiSerializer(team_notis_by_month_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamSchedules(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        try:
            team = self.get_object(pk)

            if team.spvsr != request.user:
                raise PermissionDenied

            # # 1. 요청에서 date와 time 값을 추출
            date_str = request.data.get('date')
            time_str = request.data.get('time')
            
            # # 2. 이 두 값을 합쳐 dateTime 필드를 생성
            date_obj = timezone.datetime.strptime(date_str, "%Y-%m-%d").date() # 예: '2023-08-23'를 date 객체로
            time_obj = timezone.datetime.strptime(time_str, "%H:%M").time() # 예: '15:30'를 time 객체로
            
            combined_datetime = timezone.datetime.combine(date_obj, time_obj)

            # 3. dateTime 필드를 직렬화기에 전달하기 전에 request 데이터에 추가
            # dateTime = combined_datetime.isoformat()
            dateTime = combined_datetime

            # dateTime = timezone.datetime.combine(date, time)

            data = request.data.copy()
            data['dateTime'] = dateTime
            data['team'] = team.id  # or whichever representation you need

            # request.data['dateTime'] = dateTime

            # serializer = TeamScheduleSerializer(data=request.data)
            serializer = TeamScheduleSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    schedule = serializer.save()

                    TeamNoti.objects.create(
                                team=team,
                                schedule=schedule,
                                dateTime=timezone.now(),
                                name="Tom",
                                description="삼오엠 매니저",
                                title=f"{schedule.title}",
                                category="plan",
                                payload="새로운 일정이 추가되었습니다.",
                            )
                    
                    serializer = TeamScheduleSerializer(schedule)

            else:
                print(serializer.errors)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TeamScheduleDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            schedule = TeamSchedule.objects.get(pk=pk)
            return schedule
        except TeamSchedule.DoesNotExist:
            raise NotFound

    def delete(self, request, pk, schedule_pk):
        schedule = self.get_object(schedule_pk)
        team = schedule.team

        if team.spvsr != request.user:
            raise PermissionDenied

        schedule.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class TeamSchedulesMonth(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)

        # 년월로 그룹화
        dates = team.schedules.annotate(month_created=TruncMonth('dateTime')).values('month_created').distinct().order_by('-month_created')

        # 결과를 'YYYY년 MM월' 형식으로 변환
        formatted_dates = [date['month_created'].strftime('%Y년 %m월') for date in dates]

        
        return Response(formatted_dates, status=status.HTTP_200_OK)


class TeamSchedulesByMonth(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        team = self.get_object(pk)
        year = request.data.get("year")
        month = request.data.get("month")

        team_schedules_all = team.schedules.all()
        team_schedules_by_month = team_schedules_all.filter(dateTime__year=year, dateTime__month=month)
        team_schedules_by_month_sorted = team_schedules_by_month.order_by("-dateTime")
        serializer = TeamScheduleSerializer(team_schedules_by_month_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeamDuesDetailList(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_dues_details_all = team.dues_details.all()
        team_dues_details_all_sorted = team_dues_details_all.order_by("-created_at")
        serializer = DuesDetailSerializer(team_dues_details_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamDuesDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        try:
            team = Team.objects.get(pk=pk)

            if team.spvsr != request.user:
                raise PermissionDenied

            data = request.data.copy()
            data['team'] = team.id

            serializer = DuesDetailSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    dues_detail = serializer.save()
                    serializer = DuesDetailSerializer(dues_detail)

            else:
                print(serializer.errors)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)



class TeamDuesDetailDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            dues_detail = DuesDetail.objects.get(pk=pk)
            return dues_detail
        except DuesDetail.DoesNotExist:
            raise NotFound

    def get(self, request, pk, detail_pk):
        try:
            dues_detail = self.get_object(detail_pk)
            serializer = DuesDetailSerializer(dues_detail)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk, detail_pk):
        try:
            dues_detail = self.get_object(detail_pk)
            serializer = DuesDetailSerializer(dues_detail, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, detail_pk):

        dues_detail = self.get_object(detail_pk)
        team = dues_detail.team

        if team.spvsr != request.user:
            raise PermissionDenied

        dues_detail.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class TeamDuesInItems(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            dues_detail = DuesDetail.objects.get(pk=pk)
            return dues_detail
        except DuesDetail.DoesNotExist:
            raise NotFound

    def get(self, request, pk, detail_pk):
        dues_detail = self.get_object(detail_pk)
        team_dues_in_items_all = dues_detail.dues_in_items.all()
        team_dues_in_items_all_sorted = team_dues_in_items_all.order_by("-date")
        serializer = DuesInItemSerializer(team_dues_in_items_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk, detail_pk):
        try:
            dues_detail = self.get_object(pk=detail_pk)
            team = Team.objects.get(pk=pk)

            if team.spvsr != request.user:
                raise PermissionDenied

            data = request.data.copy()
            data['dues_detail'] = dues_detail.id

            serializer = DuesInItemSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    dues_in_item = serializer.save()
                    serializer = DuesInItemSerializer(dues_in_item)

            else:
                print(serializer.errors)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TeamDuesInItemDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            dues_in_item = DuesInItem.objects.get(pk=pk)
            return dues_in_item
        except DuesInItem.DoesNotExist:
            raise NotFound

    def delete(self, request, pk, item_pk):
        dues_in_item = self.get_object(item_pk)
        dues_detail = dues_in_item.dues_detail
        team = dues_detail.team

        if team.spvsr != request.user:
            raise PermissionDenied

        dues_in_item.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class TeamDuesInAmount(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            dues_detail = DuesDetail.objects.get(pk=pk)
            return dues_detail
        except DuesDetail.DoesNotExist:
            raise NotFound

    def get(self, request, pk, detail_pk):
        dues_detail = self.get_object(detail_pk)
        team_dues_in_items_all = dues_detail.dues_in_items.all()

        dues_in_amount = sum(item.amount for item in team_dues_in_items_all)

        return Response({"amount": dues_in_amount},  status=status.HTTP_200_OK)

class TeamDuesOutItems(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            dues_detail = DuesDetail.objects.get(pk=pk)
            return dues_detail
        except DuesDetail.DoesNotExist:
            raise NotFound

    def get(self, request, pk, detail_pk):
        dues_detail = self.get_object(detail_pk)
        team_dues_out_items_all = dues_detail.dues_out_items.all()
        team_dues_out_items_all_sorted = team_dues_out_items_all.order_by("-date")
        serializer = DuesOutItemSerializer(team_dues_out_items_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk, detail_pk):
        try:
            dues_detail = self.get_object(pk=detail_pk)
            team = Team.objects.get(pk=pk)

            if team.spvsr != request.user:
                raise PermissionDenied

            data = request.data.copy()
            data['dues_detail'] = dues_detail.id

            serializer = DuesOutItemSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    dues_out_item = serializer.save()
                    serializer = DuesOutItemSerializer(dues_out_item)

            else:
                print(serializer.errors)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class TeamDuesOutItemDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            dues_out_item = DuesOutItem.objects.get(pk=pk)
            return dues_out_item
        except DuesOutItem.DoesNotExist:
            raise NotFound

    def delete(self, request, pk, item_pk):
        dues_out_item = self.get_object(item_pk)
        dues_detail = dues_out_item.dues_detail
        team = dues_detail.team

        if team.spvsr != request.user:
            raise PermissionDenied

        dues_out_item.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamDuesOutAmount(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            dues_detail = DuesDetail.objects.get(pk=pk)
            return dues_detail
        except DuesDetail.DoesNotExist:
            raise NotFound

    def get(self, request, pk, detail_pk):
        dues_detail = self.get_object(detail_pk)
        team_dues_out_items_all = dues_detail.dues_out_items.all()

        dues_out_amount = sum(item.amount for item in team_dues_out_items_all)

        return Response({"amount": dues_out_amount},  status=status.HTTP_200_OK)


class TeamDuesPaymentList(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        team = self.get_object(pk)
        team_dues_payments_all = team.dues_payments.all()
        team_dues_payments_all_sorted = team_dues_payments_all.order_by("-created_at")
        serializer = DuesPaymentSerializer(team_dues_payments_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamDuesPayment(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            team = Team.objects.get(pk=pk)
            return team
        except Team.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        try:
            team = Team.objects.get(pk=pk)

            if team.spvsr != request.user:
                raise PermissionDenied

            data = request.data.copy()
            data['team'] = team.id

            serializer = DuesPaymentSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    dues_payment = serializer.save()

                    # 여기서 Team에 속한 모든 Player에 대해 DuesPaymentItem을 생성합니다.
                    players = team.players.all()  # team과 player 간의 연결을 어떻게 했는지에 따라 다를 수 있으므로 적절하게 수정해주세요.
                    for player in players:
                        DuesPaymentItem.objects.create(
                            dues_payment=dues_payment,
                            player=player,
                            payment=DuesPaymentItem.DuesPaymentItemChoices.NON_PAID
                        )

                    # 마지막에 다시 DuesPayment 객체에 대한 serializer를 만들어 응답을 전달합니다.
                    serializer = DuesPaymentSerializer(dues_payment)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TeamDuesPaymentDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            dues_payment = DuesPayment.objects.get(pk=pk)
            return dues_payment
        except DuesPayment.DoesNotExist:
            raise NotFound

    def get(self, request, pk, payment_pk):
        try:
            dues_payment = self.get_object(payment_pk)
            serializer = DuesPaymentSerializer(dues_payment)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, payment_pk):
        try:
            dues_payment = self.get_object(payment_pk)
            serializer = DuesPaymentSerializer(dues_payment, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, payment_pk):

        dues_payment = self.get_object(payment_pk)
        team = dues_payment.team

        if team.spvsr != request.user:
            raise PermissionDenied

        dues_payment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class TeamDuesPaymentItems(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            dues_payment = DuesPayment.objects.get(pk=pk)
            return dues_payment
        except DuesPayment.DoesNotExist:
            raise NotFound

    def get(self, request, pk, payment_pk):
        dues_payment = self.get_object(payment_pk)
        # annotate를 사용해 payment_order 필드를 추가
        team_dues_payment_items_all = dues_payment.dues_payment_items.annotate(
            payment_order=Case(
                When(payment=DuesPaymentItem.DuesPaymentItemChoices.PAID, then=Value(2)),
                When(payment=DuesPaymentItem.DuesPaymentItemChoices.NON_PAID, then=Value(1)),
                When(payment=DuesPaymentItem.DuesPaymentItemChoices.NA, then=Value(3)),
                default=Value(4),  # 혹시 모를 다른 값들에 대해
                output_field=IntegerField()
            )
        ).order_by("payment_order", "-created_at")  # 먼저 payment_order로 정렬한 후 동일한 카테고리 내에서 created_at으로 정렬
        serializer = DuesPaymentItemSerializer(team_dues_payment_items_all, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk, payment_pk):
        try:
            dues_payment = self.get_object(pk=payment_pk)
            team = Team.objects.get(pk=pk)

            if team.spvsr != request.user:
                raise PermissionDenied

            data = request.data.copy()
            data['dues_payment'] = dues_payment.id
            data['payment'] = DuesPaymentItem.DuesPaymentItemChoices.NON

            serializer = UploadDuesPaymentItemSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    dues_payment_item = serializer.save()
                    serializer = UploadDuesPaymentItemSerializer(dues_payment_item)

            else:
                print(serializer.errors)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TeamDuesPaymentItemDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            dues_payment_item = DuesPaymentItem.objects.get(pk=pk)
            return dues_payment_item
        except DuesPaymentItem.DoesNotExist:
            raise NotFound

    def get(self, request, pk, item_pk):
        try:
            dues_payment_item = self.get_object(item_pk)
            serializer = DuesPaymentItemSerializer(dues_payment_item)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk, item_pk):
        try:
            dues_payment_item = self.get_object(item_pk)
            serializer = DuesPaymentItemSerializer(dues_payment_item, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, item_pk):
        dues_payment_item = self.get_object(item_pk)
        dues_payment = dues_payment_item.dues_payment
        team = dues_payment.team

        if team.spvsr != request.user:
            raise PermissionDenied

        dues_payment_item.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamDuesPaymentItemsExtra(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            dues_payment = DuesPayment.objects.get(pk=pk)
            return dues_payment
        except DuesPayment.DoesNotExist:
            raise NotFound

    def get(self, request, pk, payment_pk):
        try:
            dues_payment = self.get_object(payment_pk)

            # dues_payment와 연결된 모든 DuesPaymentItem에서 Player들을 가져옴
            connected_players_ids = dues_payment.dues_payment_items.all().values_list('player__id', flat=True)

            # 해당 dues_payment가 가리키고 있는 team의 모든 Player들 중에서 dues_payment와 연결되지 않은 Player들만 필터링
            unconnected_players = Player.objects.filter(team=dues_payment.team).exclude(id__in=connected_players_ids)

            unconnected_players_sorted = unconnected_players.order_by("backnumber")

            # 응답을 위해 Player 객체를 serialize. 여기서는 간단하게 이름만 반환하였지만, 필요에 따라 다른 필드나 전체 데이터를 반환할 수 있음
            data = [{"id": player.id, "name": player.name, "backnumber": player.backnumber} for player in unconnected_players_sorted]

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

