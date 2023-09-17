from django.db import models
from common.models import CommonModel

# Create your models here.

class TeamVoteBallot(CommonModel):
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="tballots")
    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="tballots")

class TeamVote(CommonModel):

    """ Model TeamVote Definition """

    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="tvotes")
    start = models.DateTimeField()
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    candidates = models.ManyToManyField("players.Player", related_name="candidated_tvotes")
    participants = models.ManyToManyField("players.Player", related_name="participated_tvotes", blank=True)
    winners = models.ManyToManyField("players.Player", related_name="winner_tvotes", blank=True)

    def __str__(self) -> str:
        return (f"{self.team}, {self.title}")

class TeamNoti(CommonModel):

    """ Model TeamFeed Definition """

    class TeamNotiCategoryChoices(models.TextChoices):
        TOM = ("tom", "Tom")
        VOTE = ("vote", "Vote")
        GAME = ("game", "Game")
        PLAN = ("plan", "Plan")
    
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="notis")
    game = models.ForeignKey("games.Game", on_delete=models.CASCADE, related_name="notis", null=True ,blank=True)
    schedule = models.ForeignKey("teams.TeamSchedule", on_delete=models.CASCADE, related_name="notis", null=True ,blank=True)
    tvote = models.ForeignKey("teams.TeamVote", on_delete=models.CASCADE, related_name="notis", null=True ,blank=True)
    dateTime = models.DateTimeField()
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=150, blank=True)
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=TeamNotiCategoryChoices.choices,)
    payload = models.TextField()

    def __str__(self) -> str:
        return f"{self.team.name}/{self.title}"

class TeamSchedule(CommonModel):

    """ Model TeamFeed Definition """

    class TeamScheduleCategoryChoices(models.TextChoices):
        PLAN = ("plan", "Plan")
        GAME = ("game", "Game")
    
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="schedules")
    game = models.ForeignKey("games.Game", on_delete=models.CASCADE, related_name="schedules", null=True, blank=True)
    dateTime = models.DateTimeField()
    category = models.CharField(max_length=20, choices=TeamScheduleCategoryChoices.choices,)
    title = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f"{self.team.name}/{self.title}"

class TeamFeed(CommonModel):

    """ Model TeamFeed Definition """
    
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="feeds")
    title = models.CharField(max_length=150)
    payload = models.TextField()

    def __str__(self) -> str:
        return f"{self.team.name}/{self.title}"


class DuesPayment(CommonModel):

    """ Model DuesPayment Definition """

    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="dues_payments")
    title = models.CharField(max_length=150)
    memo = models.TextField(blank=True)

class DuesPaymentItem(CommonModel):

    """ Model DuesPaymentItem Definition """

    class DuesPaymentItemChoices(models.TextChoices):
        PAID = ("paid", "Paid")
        NON_PAID = ("non_paid", "Non_Paid")
        NA = ("na", "Na")

    dues_payment = models.ForeignKey("teams.DuesPayment", on_delete=models.CASCADE, related_name="dues_payment_items")
    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="dues_payment_items")
    payment = models.CharField(max_length=20, choices=DuesPaymentItemChoices.choices)


class DuesDetail(CommonModel):

    """ Model DuesDetail Definition """

    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="dues_details")
    title = models.CharField(max_length=150)
    memo = models.TextField(blank=True)
    carry_over = models.PositiveIntegerField(blank=True)


class DuesInItem(CommonModel):

    """ Model DuesInItem Definition """

    dues_detail = models.ForeignKey("teams.DuesDetail", on_delete=models.CASCADE, related_name="dues_in_items")
    title = models.CharField(max_length=150)
    date = models.DateField()
    amount = models.PositiveIntegerField()
    note = models.CharField(max_length=150, blank=True)

class DuesOutItem(CommonModel):

    """ Model DuesOutItem Definition """

    dues_detail = models.ForeignKey("teams.DuesDetail", on_delete=models.CASCADE, related_name="dues_out_items")
    title = models.CharField(max_length=150)
    date = models.DateField()
    amount = models.PositiveIntegerField()
    note = models.CharField(max_length=150, blank=True)


class Team(CommonModel):

    """ Model Team Definition """

    avatar = models.URLField(blank=True)
    name = models.CharField(max_length=150, unique=True)
    description = models.CharField(max_length=150, blank=True)
    since = models.PositiveIntegerField()
    spvsr = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="team", default=None)
    plan = models.CharField(max_length=150, default="basic",)
    code = models.PositiveIntegerField()

    def __str__(self) -> str:
        return self.name

class Ball(CommonModel):

    """ Model Ball Definition """

    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="balls")
    is_used = models.BooleanField(default=False)

    def __str__(self) -> str:
        return (f"{self.team.name} / Ball ")