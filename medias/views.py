import re
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Photo, Video
import requests
from django.conf import settings

# Create your views here.

class GetUploadURL(APIView):

    def post(self, request):
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CF_ID}/images/v2/direct_upload"

        result_obj = requests.post(url, 
                                        headers={
                                            "Authorization" : f"Bearer {settings.CF_TOKEN}"
                                        })

        result = (result_obj.json()).get("result")
            # one_time_url_obj -> result 에는 ID, URL이 들어있음
        
        return Response({"id" : result.get("id"), "uploadURL" : result.get("uploadURL")})

class Photos(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            photo = Photo.objects.get(pk=pk)
            return photo
        except Photo.DoesNotExist:
            raise NotFound

    def delete(self, request, pk):

        photo = self.get_object(pk)
        team = photo.team
        user = request.user

        if not team.spvsrs.filter(id=user.id).exists():
            raise PermissionDenied

        def extract_image_id_from_url(url: str) -> str:
            pattern = r"([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})"
            match = re.search(pattern, url)
            if match:
                return match.group(1)
            return None

        if photo.file:

            image_id = extract_image_id_from_url(photo.file)

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

        photo.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class Videos(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            video = Video.objects.get(pk=pk)
            return video
        except Video.DoesNotExist:
            raise NotFound

    def delete(self, request, pk):

        video = self.get_object(pk)
        team = video.team
        user = request.user

        if not team.spvsrs.filter(id=user.id).exists():
            raise PermissionDenied

        video.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)