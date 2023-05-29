from rest_framework import serializers
from .models import Player
from teams.serializers import TinyTeamSerializer

class TinyPlayerSerializer(serializers.ModelSerializer):

    is_connecting = serializers.SerializerMethodField()
    is_connected = serializers.SerializerMethodField()


    def get_is_connecting(self, player):
        if player.connecting_user:
            return True
        return False

    def get_is_connected(self, player):
        if player.connected_user:
            return True
        return False


    class Meta:
        model = Player
        fields = (
            "pk",
            "team",
            "avatar",
            "backnumber",
            "name",
            "is_connecting",
            "is_connected"
        )

class PlayerSerializer(serializers.ModelSerializer):

    team = TinyTeamSerializer()
    # games = TinyGameSerializer(many=True)
    # tom_games = TinyGameSerializer(many=True)
    superplayers = TinyPlayerSerializer(many=True)
    # goals = GoalPlayerSerializer(many=True)

    class Meta:
        model = Player
        depth = 1
        fields = "__all__"