# Generated by Django 4.1.3 on 2023-10-27 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_topspot_feature'),
    ]

    operations = [
        migrations.AddField(
            model_name='topspot',
            name='image',
            field=models.ImageField(default='', upload_to=''),
            preserve_default=False,
        ),
    ]