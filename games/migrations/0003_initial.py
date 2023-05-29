# Generated by Django 4.2.1 on 2023-05-17 21:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('games', '0002_initial'),
        ('teams', '0001_initial'),
        ('players', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='teams.team'),
        ),
        migrations.AddField(
            model_name='game',
            name='toms',
            field=models.ManyToManyField(blank=True, related_name='tom_games', to='players.player'),
        ),
    ]
