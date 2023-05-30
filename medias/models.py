from django.db import models
from common.models import CommonModel

# Create your models here.

class Photo(CommonModel):

    """ Model Photo Definition """

    file = models.URLField()
    player = models.ForeignKey("players.Player", null=True, blank=True, on_delete=models.CASCADE, related_name="photos")
    team = models.ForeignKey("teams.Team", null=True, blank=True, on_delete=models.CASCADE, related_name="photos")

    def __str__(self) -> str:
        return "Photo File"