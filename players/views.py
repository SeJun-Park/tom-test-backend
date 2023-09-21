import time
import requests
import re
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from rest_framework import status
from .models import Player
from games.models import Game
from .serializers import PlayerSerializer, UploadPlayerSerializer
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

    def put(self, request, pk):
        
        player = self.get_object(pk)
        user = request.user

        if user.is_player:

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
        
        if player.team:
            team = player.team

        if player.game:
            team = player.game.team

        user = request.user

        if not team.spvsrs.filter(id=user.id).exists():
            raise PermissionDenied

        player.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class PlayerPhoto(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            player = Player.objects.get(pk=pk)
            return player
        except Player.DoesNotExist:
            raise NotFound

    def put(self, request, pk):

        player = self.get_object(pk=pk)
        team = player.team
        user = request.user

        if not team.spvsrs.filter(id=user.id).exists():
            raise PermissionDenied

        def extract_image_id_from_url(url: str) -> str:
            pattern = r"([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})"
            match = re.search(pattern, url)
            if match:
                return match.group(1)
            return None

        print(request.data)

        if player.avatar and request.data.get("avatar"):

            image_id = extract_image_id_from_url(player.avatar)

            if image_id:
                url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CF_ID}/images/v1/{image_id}"
            
                response = requests.delete(url, headers={
                        "Authorization": f"Bearer {settings.CF_TOKEN}",
                        "Content-Type": "application/json"
                        # "X-Auth-Email": "sejun9aldo@gmail.com",
                        # "X-Auth-Key": settings.CF_GLOBAL_API_KEY
                })


                if response.status_code != 200:  # 204 No Content는 성공적으로 삭제되었음을 의미합니다.
                    return Response({"error": "Failed to delete image", "details": response.text}, status=response.status_code)

        serializer = UploadPlayerSerializer(player, data=request.data, partial=True)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    player = serializer.save()

            except Exception as e: 
                # 어떤 에러가 나든지 라는 뜻.
                print(e)
                raise ParseError

            serializer = UploadPlayerSerializer(player)

            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            print(f"serializer.errors : {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        permission_classes = [IsAuthenticated]
            
        player = self.get_object(pk=pk)
        team = player.team
        user = request.user

        if not team.spvsrs.filter(id=user.id).exists():
            raise PermissionDenied

        def extract_image_id_from_url(url: str) -> str:
            pattern = r"([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})"
            match = re.search(pattern, url)
            if match:
                return match.group(1)
            return None

        if player.avatar:

            image_id = extract_image_id_from_url(player.avatar)

            if image_id:
                url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CF_ID}/images/v1/{image_id}"
            
                response = requests.delete(url, headers={
                        "Authorization": f"Bearer {settings.CF_TOKEN}",
                        "Content-Type": "application/json"
                        # "X-Auth-Email": "sejun9aldo@gmail.com",
                        # "X-Auth-Key": settings.CF_GLOBAL_API_KEY
                })


                if response.status_code != 200:  # 204 No Content는 성공적으로 삭제되었음을 의미합니다.
                    return Response({"error": "Failed to delete image", "details": response.text}, status=response.status_code)

                player.avatar = ""
                player.save()
                
            return Response({"message": "Image successfully deleted and avatar cleared."}, status=status.HTTP_200_OK)    

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