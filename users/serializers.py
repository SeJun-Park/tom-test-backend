from rest_framework import serializers
from .models import User
from teams.serializers import TinyTeamSerializer
from players.serializers import TinyPlayerSerializer

class TinyUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "username",
            "is_player",
            "is_spvsr",
        )

class MeUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = (
            "password",
            "is_superuser",
            "id",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
        )

class IsPlayerUserSerializer(serializers.ModelSerializer):

    connected_players = TinyPlayerSerializer(many=True)
    connecting_players = TinyPlayerSerializer(many=True)

    class Meta:
        model = User
        exclude = (
            "password",
            "is_superuser",
            "id",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
        )

class SpvsrUserSerializer(serializers.ModelSerializer):

    is_founder = serializers.SerializerMethodField()

    def get_is_founder(self, user):
        team = self.context.get("team")

        if team:
            return (team.founder == user)
        return False

    class Meta:
        model = User
        fields = (
                "last_login",
                "id",
                "username",
                "avatar",
                "email",
                "avatar",
                "is_player",
                "is_spvsr",
                "is_founder",
                "date_joined",
        )

class IsSpvsrUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = (
            "password",
            "is_superuser",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
        )