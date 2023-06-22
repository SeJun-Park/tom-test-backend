from django.db import models
from common.models import CommonModel

# Create your models here.

class Photo(CommonModel):

    """ Model Photo Definition """

    file = models.URLField()
    game = models.ForeignKey("games.Game", null=True, blank=True, on_delete=models.CASCADE, related_name="photos")
    team = models.ForeignKey("teams.Team", null=True, blank=True, on_delete=models.CASCADE, related_name="photos")

    def __str__(self) -> str:
        return "Photo File"

class Video(CommonModel):

    """ Model Photo Definition """

    file = models.URLField()
    game = models.ForeignKey("games.Game", null=True, blank=True, on_delete=models.CASCADE, related_name="videos")
    team = models.ForeignKey("teams.Team", null=True, blank=True, on_delete=models.CASCADE, related_name="videos")

    def __str__(self) -> str:
        return "Video File"