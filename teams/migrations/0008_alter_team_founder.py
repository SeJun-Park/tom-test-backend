# Generated by Django 4.2.1 on 2023-09-21 02:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('teams', '0007_remove_team_spvsr_team_founder_team_spvsrs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='founder',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='team_founder', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]