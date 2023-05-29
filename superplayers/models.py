from django.db import models
from common.models import CommonModel

# Create your models here.

class SuperPlayer(CommonModel):

    """ Model Superplayer Definition """

    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="superplayers")
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="superplayers")

    def __str__(self) -> str:
        return self.player.name