# Generated by Django 4.2.1 on 2023-09-13 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0010_gamequota_gamequotalineup_gamequota_lineups'),
        ('teams', '0004_team_description'),
        ('players', '0003_player_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='daily_players', to='games.game'),
        ),
        migrations.AlterField(
            model_name='player',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='players', to='teams.team'),
        ),
    ]