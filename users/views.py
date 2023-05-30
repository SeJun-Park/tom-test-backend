import time
import requests
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from .models import User
from games.models import Game, GoalPlayer
from teams.models import Team
from players.models import Player
from superplayers.models import SuperPlayer
from .serializers import MeUserSerializer, IsPlayerUserSerializer, IsSpvsrUserSerializer, SpvsrUserSerializer
from games.serializers import TinyGameSerializer
from teams.serializers import TinyTeamSerializer
from players.serializers import PlayerSerializer
from superplayers.serializers import SuperPlayerSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# Create your views here.

class Me(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = MeUserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = MeUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            serializer = MeUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class LogOut(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"ok" : "bye"})

class IsPlayerKakaoLogIn(APIView):

    def post(self, request):
        try:
            code = request.data.get("code")
            access_token_obj = requests.post("https://kauth.kakao.com/oauth/token",
            headers= {
                "Content-Type" : "application/x-www-form-urlencoded",
            },
            data={
                "grant_type" : "authorization_code",
                "client_id" : "d2703f278acadc861b3685bb7368adfb",
                "redirect_uri" : "https://tom-test-frontend.onrender.com/kakaologin",
                # "redirect_uri" : "http://127.0.0.1:3001/kakaologin",
                "code" : code
            })

            # requests.post(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id=64cd8b7236c0438cc41264f535c2b475&redirect_uri=http://127.0.0.1:3000/social/kakao&code={code}",
            # 을 위와 같이 data= 로 표현

            access_token = access_token_obj.json().get("access_token")

            raw_user_data = requests.get("https://kapi.kakao.com/v2/user/me", 
            headers={
                "Authorization" : f"Bearer {access_token}",
                "Content-type" : "application/x-www-form-urlencoded;charset=utf-8"
            })

            user_data = raw_user_data.json()
            print(user_data)
            kakao_account = user_data.get("kakao_account")
                # kakao_account 안에는 profile, email 이 있고, profile 안에는 nickname, thumnail_image_url, profile_image_url 등이 있음
            profile = kakao_account.get("profile")
        
            try:
                user = User.objects.get(email=kakao_account.get("email"), is_player=True)
                login(request, user)
                return Response(status=status.HTTP_200_OK)

            except User.DoesNotExist:
                user = User.objects.create(
                    email = kakao_account.get("email"),
                    username = profile.get("nickname"),
                    avatar = profile.get("profile_image_url"),
                    is_player = True
                )

                user.set_unusable_password()
                user.save()
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            print("-------------------------------")
            print(e)
            print("-------------------------------")
            return Response(status=status.HTTP_400_BAD_REQUEST)

class IsPlayer(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = IsPlayerUserSerializer(user)
        return Response(serializer.data)

class IsPlayerTeams(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        connected_players = user.connected_players.all()

        player_teams = Team.objects.filter(players__in=connected_players)
        player_teams_sorted = player_teams.order_by("name")

        serializer = TinyTeamSerializer(player_teams_sorted, many=True)

        return Response(serializer.data)


class IsPlayerGames(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        connected_players = user.connected_players.all()

        player_games_all = Game.objects.filter(participants__in=connected_players)
        player_games_all_sorted = player_games_all.order_by("-date")

        serializer = TinyGameSerializer(player_games_all_sorted, many=True)

        return Response(serializer.data)

class IsPlayerGoalGames(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        connected_players = user.connected_players.all()

        player_goal_games_all = Game.objects.filter(goals__player__in=connected_players).distinct()
        player_goal_games_all_sorted = player_goal_games_all.order_by("-date")
        serializer = TinyGameSerializer(player_goal_games_all_sorted, many=True)

        return Response(serializer.data)

class IsPlayerGoals(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        connected_players = user.connected_players.all()

        team_goals_all = GoalPlayer.objects.filter(player__in=connected_players).count()
        response_data = {
            "goals" : team_goals_all
        }
        return Response(response_data, status=status.HTTP_200_OK)

class IsPlayerToms(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        connected_players = user.connected_players.all()
        player_tom_games_all = Game.objects.filter(toms__in=connected_players).distinct()
        player_tom_games_all_sorted = player_tom_games_all.order_by("-date")

        serializer = TinyGameSerializer(player_tom_games_all_sorted, many=True)

        return Response(serializer.data)

class IsPlayerSuperPlayers(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        connected_players = user.connected_players.all()

        superplayers = SuperPlayer.objects.filter(player__in=connected_players)
        superplayers_sorted = superplayers.order_by("-created_at")

        serializer = SuperPlayerSerializer(superplayers_sorted, many=True)

        return Response(serializer.data)

class IsSpvsrLogIn(APIView):
    
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            raise ParseError

        user = authenticate(request=request, username=username, password=password)
        if user:
            login(request, user)
            return Response({"ok" : "Welcome!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error" : "wrong Password"}, status=status.HTTP_400_BAD_REQUEST)

class Spvsrs(APIView):

    def post(self, request):

        password = request.data.get("password")
        if not password:
            raise ParseError

        serializer = SpvsrUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save(is_spvsr=True)

            user.set_password(password)
            user.save()

            serializer = SpvsrUserSerializer(user)
            login(request, user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IsSpvsr(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = IsSpvsrUserSerializer(user)
        return Response(serializer.data)
        

class IsSpvsrTeam(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            team = user.team

            serializer = TinyTeamSerializer(team)

            return Response(serializer.data)
        except Team.DoesNotExist:
            raise NotFound

class IsSpvsrGames(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            team = user.team

            team_games_all = Game.objects.filter(team=team)
            team_games_all_sorted = team_games_all.order_by("-date")

            serializer = TinyGameSerializer(team_games_all_sorted, many=True)

            return Response(serializer.data)
        except Team.DoesNotExist:
            raise NotFound


class IsSpvsrGoals(APIView):
    pass

class IsSpvsrToms(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            team = user.team

            team_games_all = Game.objects.filter(team=team)
            team_tom_games_all = team_games_all.filter(toms__isnull=False).distinct()
            team_tom_games_all_sorted = team_tom_games_all.order_by("-date")

            serializer = TinyGameSerializer(team_tom_games_all_sorted, many=True)

            return Response(serializer.data)
        except Team.DoesNotExist:
            raise NotFound

class IsSpvsrSuperPlayers(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            team = user.team

            team_superplayers_all = SuperPlayer.objects.filter(team=team)
            team_superplayers_all_sorted = team_superplayers_all.order_by("-created_at")

            serializer = SuperPlayerSerializer(team_superplayers_all_sorted, many=True)
            
            return Response(serializer.data)
        except Team.DoesNotExist:
            raise NotFound