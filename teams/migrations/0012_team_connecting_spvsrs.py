# Generated by Django 4.2.1 on 2023-09-27 21:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teams', '0011_alter_team_founder_alter_team_spvsrs'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='connecting_spvsrs',
            field=models.ManyToManyField(blank=True, related_name='connecting_teams', to=settings.AUTH_USER_MODEL),
        ),
    ]
