import time
from django.utils.timezone import activate, get_current_timezone
from collections import Counter
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from rest_framework import status
from .models import Game, Vote, GoalPlayer, VoteBallot
from players.models import Player
from .serializers import GameSerializer, UploadGameSerializer, VoteSerializer

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# Create your views here.

class GameDetail(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            game = Game.objects.get(pk=pk)
            return game
        except Game.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        game = self.get_object(pk)
        serializer = GameSerializer(game, context={"request" : request})
        return Response(serializer.data)

    def put(self, request, pk):

        game = self.get_object(pk)

        if game.team.spvsr != request.user:
            raise PermissionDenied
         
        print(request.data)

        serializer = UploadGameSerializer(game, data=request.data, partial=True)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    game = serializer.save()

                    participants = request.data.get("participants")

                    if participants:
                        game.participants.clear()
                        for participant_pk in participants:
                            participant = Player.objects.get(pk=participant_pk)
                            game.participants.add(participant)

                    goals = request.data.get("goals")

                    if goals:
                        GoalPlayer.objects.filter(game=game).delete()
                        for goalplayer_pk in goals:
                            try:
                                player = Player.objects.get(pk=goalplayer_pk)

                                GoalPlayer.objects.create(
                                    player=player,
                                    game=game
                                )
                            except Player.DoesNotExist:
                                raise NotFound

                    serializer = UploadGameSerializer(game)

                    return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e: 
                # 어떤 에러가 나든지 라는 뜻.
                print(e)
                raise ParseError
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        game = self.get_object(pk)
        team = game.team

        if team.spvsr != request.user:
            raise PermissionDenied

        game.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class GameVote(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            vote = Vote.objects.get(game__pk=pk)
            return vote
        except Vote.DoesNotExist:
            raise NotFound
        
    def get(self, request, pk):
        vote = self.get_object(pk)
        serializer = VoteSerializer(vote, context={"request" : request})
        return Response(serializer.data)

    def put(self, request, pk):

        vote = self.get_object(pk)
        game = vote.game
        team = game.team
        user = request.user

        try:
            player = Player.objects.get(team=team, connected_user=user)
            if not player in vote.candidates.all():
                raise PermissionDenied

        except Player.DoesNotExist:
            raise NotFound

        try:
            game = Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            raise NotFound

        ballots = request.data.get("ballots")

        if ballots:
            for ballot in ballots:
                try:
                    tomPlayer = Player.objects.get(pk=ballot)

                    VoteBallot.objects.create(
                        player=tomPlayer,
                        game=game
                    )
                except Player.DoesNotExist:
                    raise NotFound
            
            result = []
            
            for voteBallot in VoteBallot.objects.filter(game=game):
                result.append(voteBallot.player.pk)

            count_dict = dict(Counter(result))
            sorted_list = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)

            game.toms.clear()

            if len(sorted_list) <= 3:

                for item in sorted_list:
                    tomPlayer_pk = item[0]
                    tomPlayer = Player.objects.get(pk=tomPlayer_pk)
                    game.toms.add(tomPlayer)

            elif len(sorted_list) > 3 & sorted_list[2][1] != sorted_list[3][1]:

                sorted_list = sorted_list[0:3]

                for item in sorted_list:
                    tomPlayer_pk = item[0]
                    tomPlayer = Player.objects.get(pk=tomPlayer_pk)
                    game.toms.add(tomPlayer)

            elif len(sorted_list) > 3 & sorted_list[2][1] == sorted_list[3][1]:

                # 대상 추출

                standard = sorted_list[2][1]
                length = len(sorted_list)
                start_index = -1
                count = 0

                for i in range(length):
                    if sorted_list[i][1] == standard and start_index == -1:
                        start_index = i

                for i in range(length):
                    if sorted_list[i][1] == standard:
                        count += 1

                end_index = start_index + count
                resort_list = sorted_list[start_index:end_index]

                # 연결 상태 우선 재배열

                for i in range(len(resort_list)):
                    player_pk = resort_list[i][0]
                    player = Player.objects.get(pk=player_pk)

                    if player.connected_user:
                        resort_list[i] = (player_pk, "connected")
                    else:
                        resort_list[i] = (player_pk, "no connected")

                for i in range(len(resort_list)):
                    if resort_list[i][1] == "no connected":
                        resort_list.append(resort_list.pop(i))

                # 재배열

                sorted_list = sorted_list[0:start_index] + resort_list + sorted_list[end_index:length]

                # 아직도 3=4 인지 검사
                if len(sorted_list) > 3 & sorted_list[2][1] == sorted_list[3][1]:

                    # 다시 대상 추출

                    standard = sorted_list[2][1]
                    length = len(sorted_list)
                    start_index = -1
                    count = 0

                    for i in range(length):
                        if sorted_list[i][1] == standard and start_index == -1:
                            start_index = i

                    for i in range(length):
                        if sorted_list[i][1] == standard:
                            count += 1

                    end_index = start_index + count
                    resort_list = sorted_list[start_index:end_index]

                    # 투표자 우선 재배열

                    for i in range(len(resort_list)):
                        player_pk = resort_list[i][0]

                        if player_pk in vote.participants:
                            resort_list[i] = (player_pk, "participants")
                        else:
                            resort_list[i] = (player_pk, "no participants")

                    for i in range(len(resort_list)):
                        if resort_list[i][1] == "no participants":
                            resort_list.append(resort_list.pop(i))

                    sorted_list = sorted_list[0:start_index] + resort_list + sorted_list[end_index:length]

                    if len(sorted_list) > 3 & sorted_list[2][1] == sorted_list[3][1]:

                        # 다시 대상 추출
                        standard = sorted_list[2][1]
                        length = len(sorted_list)
                        start_index = -1
                        count = 0

                        for i in range(length):
                            if sorted_list[i][1] == standard and start_index == -1:
                                start_index = i

                        for i in range(length):
                            if sorted_list[i][1] == standard:
                                count += 1

                        end_index = start_index + count
                        resort_list = sorted_list[start_index:end_index]

                        # 참여 경기 순 재배열

                        for i in range(len(resort_list)):
                            player_pk = resort_list[i][0]
                            player = Player.objects.get(pk=player_pk)
                            resort_list[i] = (player_pk, len(player.games.all()))

                        resort_list = sorted(resort_list, key=lambda x: x[1], reverse=True)
                        sorted_list = sorted_list[0:start_index] + resort_list + sorted_list[end_index:length]

                        # 이젠 그냥 자른다.

                # 3!=4 이면 tom 선정
                sorted_list = sorted_list[0:3]

                for item in sorted_list:
                    tomPlayer_pk = item[0]
                    tomPlayer = Player.objects.get(pk=tomPlayer_pk)
                    game.toms.add(tomPlayer)

            vote.participants.add(player)

            # timezone.activate('Asia/Seoul')  # 원하는 타임존 설정
            # now = timezone.now()

            # if (vote.candidates.count()/2) > vote.participants.count():
            #     game.toms.clear()

            if vote.candidates.count() == vote.participants.count():
                vote_end = timezone.now()
                vote.vote_end = vote_end
                vote.save()

        return Response(status=status.HTTP_200_OK)

        

class GameVoteBallot(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        pass