from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = (
        (
            None,
            # fieldset 이름
            {
                "fields" : ("email", "avatar", "username", "password", "is_player", "is_spvsr", ),
                "classes" : ("wide",),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login", 
                    "date_joined"
                    ),
                "classes": (
                "collapse",
                ),
            },
        ),
    )
    list_display = ("username", "is_player", "is_spvsr", )