import time
from django.db.models import Count
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
from .models import Team
from players.models import Player
from games.models import Game, GoalPlayer, Vote
from .serializers import TeamSerializer, TinyTeamSerializer
from players.serializers import TinyPlayerSerializer
from games.serializers import TinyGameSerializer, UploadGameSerializer
from superplayers.serializers import SuperPlayerSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# Create your views here.

class Teams(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            team = serializer.save(spvsr=user)
            serializer = TeamSerializer(team, context={"request" : request})
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
            player_name = request.data.get("name")
            player_backnumber = request.data.get("backnumber")

            player = Player.objects.create(
                team=team,
                name=player_name,
                backnumber=player_backnumber
            )

            player.save()

            return Response(status=status.HTTP_200_OK)
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
        print(request.data)
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
        team_games_all = team.games.all()
        team_toms_all = team_games_all.filter(toms__isnull=False).distinct()
        team_toms_all_sorted = team_toms_all.order_by("-date")
        serializer = TinyGameSerializer(team_toms_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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