from rest_framework import serializers
from .models import Team, Ball, TeamFeed, TeamNoti, TeamSchedule, TeamVote, DuesDetail, DuesPayment, DuesInItem, DuesOutItem, DuesPaymentItem
from medias.serializers import PhotoSerializer

class TinyTeamSerializer(serializers.ModelSerializer):

    is_spvsr = serializers.SerializerMethodField()

    def get_is_spvsr(self, team):
        request = self.context.get("request")
        if request:
            user = request.user
            return team.spvsrs.filter(id=user.id).exists()
        return False

    class Meta:
        model = Team
        fields = (
            "pk",
            "avatar",
            "description",
            "name",
            "since",
            "is_spvsr"
        )

class TeamSerializer(serializers.ModelSerializer):

    # players = 
    # games = 
    # balls = 
    # spvsr = TinyUserSerializer()

    is_connected = serializers.SerializerMethodField()
    is_connected_player_pk = serializers.SerializerMethodField()
    is_connecting = serializers.SerializerMethodField()
    is_connecting_player_pk = serializers.SerializerMethodField()
    is_spvsr = serializers.SerializerMethodField()
    is_connecting_spvsr = serializers.SerializerMethodField()
    is_founder = serializers.SerializerMethodField()

    def get_is_connected(self, team):
        request = self.context.get("request")
        if request:
            user = request.user
            is_connected = user.connected_players.filter(team=team).exists()
            return is_connected
        return False

    def get_is_connected_player_pk(self, team):
        request = self.context.get("request")
        if request:
            user = request.user
            try:
                is_connected_player = user.connected_players.get(team=team)
                is_connected_player_pk = is_connected_player.pk
                return is_connected_player_pk
            except Exception as e:
                return 0
        return 0

    def get_is_connecting(self, team):
        request = self.context.get("request")
        if request:
            user = request.user
            is_connecting = user.connecting_players.filter(team=team).exists()
            return is_connecting
        return False

    def get_is_connecting_player_pk(self, team):
        request = self.context.get("request")
        if request:
            user = request.user
            try:
                is_connecting_player = user.connecting_players.get(team=team)
                is_connecting_player_pk = is_connecting_player.pk
                return is_connecting_player_pk
            except Exception as e:
                return 0
        return 0

    def get_is_spvsr(self, team):
        request = self.context.get("request")
        if request:
            user = request.user
            return team.spvsrs.filter(id=user.id).exists()
        return False

    def get_is_connecting_spvsr(self, team):
        request = self.context.get("request")
        if request:
            user = request.user
            return team.connecting_spvsrs.filter(id=user.id).exists()
        return False

    def get_is_founder(self, team):
        request = self.context.get("request")
        if request:
            user = request.user
            return (team.founder == user)
        return False

    class Meta:
        model = Team
        fields = "__all__"

class UploadTeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = "__all__"

class BallSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ball
        fields = "__all__"

class UploadTeamFeedSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TeamFeed
        fields = "__all__"

class TeamFeedSerializer(serializers.ModelSerializer):

    photos = PhotoSerializer(many=True)

    class Meta:
        model = TeamFeed
        fields = "__all__"

class TeamNotiSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeamNoti
        fields = "__all__"

class TeamScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeamSchedule
        fields = "__all__"

class TeamVoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeamVote
        fields = "__all__"

class DuesDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DuesDetail
        fields = "__all__"

class DuesPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = DuesPayment
        fields = "__all__"

class DuesInItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = DuesInItem
        fields = "__all__"

class DuesOutItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = DuesOutItem
        fields = "__all__"

class DuesPaymentItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = DuesPaymentItem
        depth = 1
        fields = "__all__"

class UploadDuesPaymentItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = DuesPaymentItem
        fields = "__all__"