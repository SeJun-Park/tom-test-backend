from django.db import models
from common.models import CommonModel

# Create your models here.

class Team(CommonModel):

    """ Model Team Definition """

    avatar = models.URLField(blank=True)
    name = models.CharField(max_length=150, unique=True)
    since = models.PositiveIntegerField(blank=True, null=True)
    description = models.CharField(max_length=150, blank=True)
    spvsr = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="team", default=None)
    plan = models.CharField(max_length=150, default="basic",)

    def __str__(self) -> str:
        return self.name

    def code(self):
        return (self.pk * 3 - 3)

class Ball(CommonModel):

    """ Model Ball Definition """

    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="balls")
    is_used = models.BooleanField(default=False)

    def __str__(self) -> str:
        return (f"{self.team.name} / Ball ")