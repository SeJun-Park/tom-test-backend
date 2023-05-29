import time
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from rest_framework import status
from .models import Player
from games.models import Game
from .serializers import PlayerSerializer
from games.serializers import TinyGameSerializer
from superplayers.serializers import SuperPlayerSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# Create your views here.


class PlayerConnecting(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            player = Player.objects.get(pk=pk)
            return player
        except Player.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        
        player = self.get_object(pk)
        user = request.user
        team_code = request.data.get("code")
        # print(type(team_code))
        # print(type(player.team.code()))
        if team_code == str(player.team.code()):

            player.connecting_user = user
            player.save()

            serializer = PlayerSerializer(player)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PlayerConnectingCancel(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            player = Player.objects.get(pk=pk)
            return player
        except Player.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        
        player = self.get_object(pk)
        player.connected_user = None
        player.connecting_user = None
        player.save()

        serializer = PlayerSerializer(player)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PlayerConnect(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            player = Player.objects.get(pk=pk)
            return player
        except Player.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        
        player = self.get_object(pk)
        user = request.user
        connecting_user = player.connecting_user
        player.connected_user = connecting_user
        player.connecting_user = None
        player.save()

        serializer = PlayerSerializer(player)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PlayerDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            player = Player.objects.get(pk=pk)
            return player
        except Player.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        player = self.get_object(pk)
        serializer = PlayerSerializer(player)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            player = self.get_object(pk)

            serializer = PlayerSerializer(player, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        player = self.get_object(pk)
        team = player.team

        if team.spvsr != request.user:
            raise PermissionDenied

        player.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class PlayerGames(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            player = Player.objects.get(pk=pk)
            return player
        except Player.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        player = self.get_object(pk)
        player_games_all = player.games.all()
        player_games_all_sorted = player_games_all.order_by("-date")
        serializer = TinyGameSerializer(player_games_all_sorted, many=True)
        return Response(serializer.data)

class PlayerGoalGames(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            player = Player.objects.get(pk=pk)
            return player
        except Player.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        player = self.get_object(pk)
        player_goal_games_all = Game.objects.filter(goals__player=player).distinct()
        player_goal_games_all_sorted = player_goal_games_all.order_by("-date")
        serializer = TinyGameSerializer(player_goal_games_all_sorted, many=True)
        return Response(serializer.data)

class PlayerGoals(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            player = Player.objects.get(pk=pk)
            return player
        except Player.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            player = self.get_object(pk)
            player_goals_all = player.goals.all().count()
            response_data = {
                "goals" : player_goals_all
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    

class PlayerTOMS(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            player = Player.objects.get(pk=pk)
            return player
        except Player.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        player = self.get_object(pk)
        player_tom_games_all = player.tom_games.all()
        player_toms_all_sorted = player_tom_games_all.order_by("-date")
        serializer = TinyGameSerializer(player_toms_all_sorted, many=True)
        return Response(serializer.data)

class PlayerSuperPlayers(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            player = Player.objects.get(pk=pk)
            return player
        except Player.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        player = self.get_object(pk)
        player_superplayers_all = player.superplayers.all()
        player_superplayers_all_sorted = player_superplayers_all.order_by("-created_at")
        serializer = SuperPlayerSerializer(player_superplayers_all_sorted, many=True)
        return Response(serializer.data)

class PlayerSuperplayerCheck(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            player = Player.objects.get(pk=pk)
            return player
        except Player.DoesNotExist:
            raise NotFound
        
    def post(self, request, pk):
        pass