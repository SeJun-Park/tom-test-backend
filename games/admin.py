from django.contrib import admin
from .models import GoalPlayer, Game, Vote, VoteBallot, GameQuota

# Register your models here.

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("team", "vsteam", "team_score", "vsteam_score", )

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    pass

@admin.register(GoalPlayer)
class GoalPlayerAdmin(admin.ModelAdmin):
    list_display = ("game", "player")

@admin.register(VoteBallot)
class VoteBallotAdmin(admin.ModelAdmin):
    list_display = ("game", "player")

@admin.register(GameQuota)
class GameQuotaAdmin(admin.ModelAdmin):
    list_display = ("game", "formation",)