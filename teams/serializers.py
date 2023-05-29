from rest_framework import serializers
from .models import Team, Ball

class TinyTeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = (
            "pk",
            "code",
            "avatar",
            "name",
            "plan",
            "since",
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
            return (team.spvsr == user)
        return False

    class Meta:
        model = Team
        fields = "__all__"

class BallSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ball
        fields = "__all__"