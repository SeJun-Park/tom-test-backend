from django.contrib import admin
from .models import SuperPlayer

# Register your models here.

@admin.register(SuperPlayer)
class SuperplayerAdmin(admin.ModelAdmin):

    pass