from django.db import models
from common.models import CommonModel

# Create your models here.

class Player(CommonModel):

    """ Model Player Definition """

    avatar = models.URLField(blank=True)
    name = models.CharField(max_length=150)
    backnumber = models.PositiveIntegerField()
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="players")
    connected_user = models.ForeignKey("users.User", blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name="connected_players")
    connected_at = models.DateTimeField(blank=True, null=True)
    connecting_user = models.ForeignKey("users.User", blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name="connecting_players")
    connecting_at = models.DateTimeField(blank=True, null=True)


    def __str__(self) -> str:
        return (f"{self.team.name} / {self.backnumber}. {self.name}")