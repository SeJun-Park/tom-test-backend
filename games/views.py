import time
from datetime import timedelta
from django.utils.timezone import activate, get_current_timezone
from collections import Counter
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from rest_framework import status
from .models import Game, Vote, GoalPlayer, VoteBallot, GameQuota, GameQuotaLineup
from players.models import Player
from players.serializers import UploadPlayerSerializer, TinyPlayerSerializer
from .serializers import GameSerializer, UploadGameSerializer, VoteSerializer, GameQuotaSerializer
from medias.serializers import VideoSerializer, PhotoSerializer
from teams.models import TeamNoti, TeamSchedule

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# Create your views here.

class GameDetail(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

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
        team = game.team
        user = request.user

        if not team.spvsrs.filter(id=user.id).exists():
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

                        if game.daily_players.all():
                            for daily_player in game.daily_players.all():
                                game.participants.add(daily_player)

                    try:
                        vote = Vote.objects.get(game=game)
                        vote.candidates.clear()
                        vote.candidates.set(game.participants.all())

                        game_datetime_start = timezone.datetime.combine(game.date, game.start_time)
                        game_datetime_end = timezone.datetime.combine(game.date, game.end_time)
                        vote_start = game_datetime_end
                        vote_end = game_datetime_end + timedelta(days=2)
                        vote_end = vote_end.replace(hour=0, minute=0, second=0)

                        vote_start = timezone.make_aware(vote_start)
                        vote_end = timezone.make_aware(vote_end)

                        vote.start = vote_start
                        vote.end = vote_end
                        vote.save()
                        
                    except Vote.DoesNotExist:
                        pass

                    try:
                        noti = TeamNoti.objects.get(team=team, game=game, category="tom")
                        noti.title = f"VS {game.vsteam}"
                        noti.dateTime = timezone.make_aware(game_datetime_end)
                        noti.save()
                    except TeamNoti.DoesNotExist:
                        pass

                    try:
                        noti = TeamNoti.objects.get(team=team, game=game, category="game")
                        noti.title = f"VS {game.vsteam}"
                        noti.dateTime = timezone.make_aware(game_datetime_end)
                        noti.save()
                    except TeamNoti.DoesNotExist:
                        pass

                    try:
                        schedule = TeamSchedule.objects.get(team=team, game=game)
                        schedule.dateTime = timezone.make_aware(game_datetime_start)
                        schedule.title = f"VS {game.vsteam}"
                        schedule.save()
                    except TeamSchedule.DoesNotExist:
                        pass

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
                print(e)
                raise ParseError
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):

        game = self.get_object(pk)
        team = game.team
        user = request.user

        if not team.spvsrs.filter(id=user.id).exists():
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

        

class GameVideos(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            game = Game.objects.get(pk=pk)
            return game
        except Game.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        try:
            game = self.get_object(pk=pk)
            team = game.team
            user = request.user

            if not team.spvsrs.filter(id=user.id).exists():
                raise PermissionDenied

            data = request.data.copy()
            data['team'] = team.id
            data['game'] = game.id

            serializer = VideoSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    video = serializer.save()
                    serializer = VideoSerializer(video)

            else:
                print(serializer.errors)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GamePhotos(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            game = Game.objects.get(pk=pk)
            return game
        except Game.DoesNotExist:
            raise NotFound
    
    def post(self, request, pk):
        game = self.get_object(pk)
        team = game.team
        user = request.user

        if not team.spvsrs.filter(id=user.id).exists():
            raise PermissionDenied

        serializer = PhotoSerializer(data=request.data)

        if serializer.is_valid():
            photo = serializer.save(team=team, game=game)

            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameDailyPlayers(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            game = Game.objects.get(pk=pk)
            return game
        except Game.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        try:
            game = self.get_object(pk=pk)
            team = game.team
            user = request.user

            if not team.spvsrs.filter(id=user.id).exists():
                raise PermissionDenied

            data = request.data.copy()
            data['backnumber'] = 0
            data['avatar'] = "https://imagedelivery.net/SbAhiipQhJYzfniSqnZDWw/4501369f-3735-4381-98b3-b81305e64300/public"

            serializer = UploadPlayerSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    player = serializer.save(game=game)
                    serializer = UploadPlayerSerializer(player)

                    game.participants.add(player)

            else:
                print(serializer.errors)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    
class GameQuotas(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            game = Game.objects.get(pk=pk)
            return game
        except Game.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        game = self.get_object(pk)
        game_quotas_all = game.quotas.all()
        game_quotas_all_sorted = game_quotas_all.order_by("created_at")
        serializer = GameQuotaSerializer(game_quotas_all_sorted, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        game = self.get_object(pk)
        
        # 요청으로부터 전달받은 데이터를 받아옵니다.
        quotas_data = request.data

        if not isinstance(quotas_data, list):
            return Response({"error": "Expected a list of quotas"}, status=status.HTTP_400_BAD_REQUEST)

        # GameQuota 인스턴스들을 담을 리스트입니다.
        quotas_to_create = []

        for quota_data in quotas_data:
            # 각각의 quota_data에 대한 유효성 검사를 진행합니다.
            if "formation" not in quota_data or "lineups" not in quota_data:
                return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

            # lineups 필드에 대한 유효성 검사
            lineup_pks = quota_data.get("lineups")
            if not isinstance(lineup_pks, list) or not all(isinstance(pk, int) for pk in lineup_pks):
                return Response({"error": "Invalid lineups data"}, status=status.HTTP_400_BAD_REQUEST)

            lineup_players = Player.objects.filter(pk__in=lineup_pks)
            if len(lineup_pks) != lineup_players.count():
                return Response({"error": "Some player IDs are invalid"}, status=status.HTTP_400_BAD_REQUEST)

            memo = quota_data.get("memo", "")
            
            # GameQuota 인스턴스를 생성하지만 데이터베이스에는 저장하지 않습니다.
            quota = GameQuota(game=game, formation=quota_data["formation"], memo=memo)
            
            # 나중에 한번에 저장하기 위해 인스턴스를 리스트에 추가합니다.
            quotas_to_create.append(quota)

        # 모든 인스턴스를 데이터베이스에 저장합니다.
        GameQuota.objects.bulk_create(quotas_to_create)

        # 이제 각 GameQuota에 대해 lineups를 설정합니다.
        for quota_data, quota in zip(quotas_data, quotas_to_create):
            # lineups 필드에 대한 Player 객체들을 조회합니다.
            for order, player_pk in enumerate(quota_data["lineups"]):
                GameQuotaLineup.objects.create(game_quota=quota, player_id=player_pk, order=order)
            
        return Response({"message": "GameQuotas created successfully"}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        game = self.get_object(pk)
        team = game.team
        user = request.user

        if not team.spvsrs.filter(id=user.id).exists():
            raise PermissionDenied

        game.quotas.all().delete()    

        return Response(status=status.HTTP_204_NO_CONTENT)


    

class GameQuotaDetail(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            game_quota = GameQuota.objects.get(pk=pk)
            return game_quota
        except GameQuota.DoesNotExist:
            raise NotFound

    def get(self, request, pk, quota_pk):
        game_quota = self.get_object(quota_pk)
        serializer = GameQuotaSerializer(game_quota)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def put(self, request, pk, quota_pk):
        try:
            game_quota = self.get_object(quota_pk)

            # lineups 필드를 별도로 처리
            lineup_pks = request.data.get("lineups", [])
            lineup_players = Player.objects.filter(pk__in=lineup_pks)
            
            # lineups 필드를 요청 데이터에서 제거
            data = {k: v for k, v in request.data.items() if k != "lineups"}
            
            serializer = GameQuotaSerializer(game_quota, data=data, partial=True)
            
            if serializer.is_valid():
                # Serializer로 데이터를 저장
                serializer.save()
                
                # ManyToMany 필드를 별도로 업데이트
                GameQuotaLineup.objects.filter(game_quota=game_quota).delete()
                for order, player_pk in enumerate(lineup_pks):
                    GameQuotaLineup.objects.create(game_quota=game_quota, player_id=player_pk, order=order)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print(serializer.errors)
            
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


