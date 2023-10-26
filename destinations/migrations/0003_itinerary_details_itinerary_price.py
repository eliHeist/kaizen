# Generated by Django 4.1.3 on 2023-10-26 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0002_alter_day_activity_alter_day_best_buy_alter_day_day_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='itinerary',
            name='details',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='itinerary',
            name='price',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
