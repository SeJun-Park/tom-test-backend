# Generated by Django 4.2.1 on 2023-07-27 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='description',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
