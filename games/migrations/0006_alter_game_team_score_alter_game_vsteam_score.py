# Generated by Django 4.2.1 on 2023-05-18 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_alter_game_team_score_alter_game_vsteam_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='team_score',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='vsteam_score',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
