from django.utils.timezone import activate, get_current_timezone
from datetime import datetime
from django.utils import timezone
from rest_framework import serializers
from .models import Game, Vote, GoalPlayer, GameQuota, GameQuotaLineup
from players.models import Player
from teams.serializers import TinyTeamSerializer
from players.serializers import TinyPlayerSerializer
from medias.serializers import VideoSerializer, PhotoSerializer

class TinyGameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        depth = 1
        fields = (
            "pk",
            "date",
            "team",
            "vsteam",
            "team_score",
            "vsteam_score",
            "toms",
        )

class VoteSerializer(serializers.ModelSerializer):

    is_candidate = serializers.SerializerMethodField()
    is_participant = serializers.SerializerMethodField()
    # is_succeeded = serializers.SerializerMethodField()

    game = TinyGameSerializer()
    candidates = TinyPlayerSerializer(many=True)

    def get_is_candidate(self, vote):

        game = vote.game
        team = game.team

        request = self.context.get("request")
        if request:
            user = request.user
            try:
                player = Player.objects.get(team=team, connected_user=user)
                return player in game.participants.all() 

            except Player.DoesNotExist:
                return False
        return False

    def get_is_participant(self, vote):
        game = vote.game
        team = game.team

        request = self.context.get("request")
        if request:
            user = request.user
            try:
                player = Player.objects.get(team=team, connected_user=user)
                return player in vote.participants.all() 

            except Player.DoesNotExist:
                return False
        return False
        

    # def get_is_succeeded(self, vote):
    #     return (vote.candidates.count()/2) <= vote.participants.count()

    class Meta:
        model = Vote
        fields = "__all__"


class GoalPlayerSerializer(serializers.ModelSerializer):

    player = TinyPlayerSerializer()
    game = TinyGameSerializer()

    class Meta:
        model = GoalPlayer
        fields = "__all__"

class GameQuotaSerializer(serializers.ModelSerializer):

    # lineups = TinyPlayerSerializer(many=True)
    lineups = serializers.SerializerMethodField()

    def get_lineups(self, game_quota):
        # lineups를 'order' 필드를 기반으로 정렬
        lineups = GameQuotaLineup.objects.filter(game_quota=game_quota).order_by('order')
        lineups = [lineup.player for lineup in lineups]
        return TinyPlayerSerializer(lineups, many=True).data


    class Meta:
        model = GameQuota
        fields = "__all__"

class GameSerializer(serializers.ModelSerializer):

    team = TinyTeamSerializer()
    goals = GoalPlayerSerializer(many=True)
    participants = TinyPlayerSerializer(many=True)
    toms = TinyPlayerSerializer(many=True)
    videos = VideoSerializer(many=True)
    photos = PhotoSerializer(many=True)
    quotas = GameQuotaSerializer(many=True)

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError("start_time should be smaller than end_time")
        return data

    class Meta:
        model = Game
        fields = "__all__"


class UploadGameSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError("start_time should be smaller than end_time")

        return data

    class Meta:
        model = Game
        fields = "__all__"