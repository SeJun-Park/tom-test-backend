from rest_framework import serializers
from .models import Photo, Video

class PhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = "__all__"

class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Video
        fields = "__all__"