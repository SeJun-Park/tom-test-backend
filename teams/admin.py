from django.contrib import admin
from .models import Team, TeamFeed, TeamNoti, TeamSchedule, TeamVote, DuesDetail, DuesPayment, DuesInItem, DuesOutItem, DuesPaymentItem

# Register your models here.

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "pk", "since", "code", "spvsr", "plan")

@admin.register(TeamNoti)
class TeamNotiAdmin(admin.ModelAdmin):
    list_display = ("team", "title", "payload")

@admin.register(TeamFeed)
class TeamFeedAdmin(admin.ModelAdmin):
    list_display = ("team", "title", "payload")

@admin.register(TeamSchedule)
class TeamScheduleAdmin(admin.ModelAdmin):
    list_display = ("team", "title", "category")

@admin.register(TeamVote)
class TeamVoteAdmin(admin.ModelAdmin):
    list_display = ("team", "title")

@admin.register(DuesDetail)
class TeamDuesDetailAdmin(admin.ModelAdmin):
    list_display = ("team", "title")

@admin.register(DuesPayment)
class TeamDuesPaymentAdmin(admin.ModelAdmin):
    list_display = ("team", "title")

@admin.register(DuesInItem)
class TeamDuesInItemAdmin(admin.ModelAdmin):
    list_display = ("dues_detail", "title")

@admin.register(DuesOutItem)
class TeamDuesOutItemAdmin(admin.ModelAdmin):
    list_display = ("dues_detail", "title")

@admin.register(DuesPaymentItem)
class TeamDuesPaymentItemAdmin(admin.ModelAdmin):
    list_display = ("player", "payment")