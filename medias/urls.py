from django.urls import path
from . import views

urlpatterns = [
    path("photos/get-url/", views.GetUploadURL.as_view()),
    path("photos/<int:pk>/", views.Photos.as_view()),
    path("videos/<int:pk>/", views.Videos.as_view())
]