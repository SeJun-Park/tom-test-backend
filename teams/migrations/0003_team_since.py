# Generated by Django 4.2.1 on 2023-05-21 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='since',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]