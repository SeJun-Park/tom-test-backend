from django.db import models
from common.models import CommonModel

# Create your models here.

class VoteBallot(CommonModel):
    game = models.ForeignKey("games.Game", on_delete=models.CASCADE, related_name="ballots")
    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="ballots")

class Vote(CommonModel):

    """ Model Vote Definition """

    game = models.OneToOneField("games.Game", on_delete=models.CASCADE, related_name="vote")
    start = models.DateTimeField()
    end = models.DateTimeField()
    candidates = models.ManyToManyField("players.Player", related_name="candidated_votes")
    participants = models.ManyToManyField("players.Player", related_name="participated_votes", blank=True)
    # toms = models.ManyToManyField("players.Player", related_name="tom_votes")

    def __str__(self) -> str:
        return (f"vote / {self.game.team} vs {self.game.vsteam}")

class GoalPlayer(CommonModel):
    game = models.ForeignKey("games.Game", on_delete=models.CASCADE, related_name="goals")
    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="goals")

class Game(CommonModel):

    """ Game Model Definition """

    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="games")
    vsteam = models.CharField(max_length=180)
    participants = models.ManyToManyField("players.Player", related_name="games")
    team_score = models.PositiveIntegerField(blank=True, null=True)
    vsteam_score = models.PositiveIntegerField(blank=True, null=True)
    location = models.CharField(max_length=180)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    toms = models.ManyToManyField("players.Player", related_name="tom_games", blank=True)

    def __str__(self) -> str:
        return (f"{self.team} vs {self.vsteam}")