# Generated by Django 4.1.3 on 2023-10-25 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0001_initial'),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopSpot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='destinations.destination')),
            ],
        ),
    ]
