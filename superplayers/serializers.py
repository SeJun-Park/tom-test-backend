from rest_framework import serializers
from .models import SuperPlayer

class SuperPlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuperPlayer
        fields = "__all__"