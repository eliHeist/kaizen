from django.db import migrations, models


def move_ugx_prices(apps, schema_editor):
    RentalItem = apps.get_model('rentals', 'RentalItem')
    for item in RentalItem.objects.exclude(currency='USD'):
        if item.currency == 'UGX':
            item.price_ugx = item.price_usd
        item.price_usd = None
        item.save(update_fields=['price_usd', 'price_ugx'])


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0001_initial'),
    ]

    operations = [
        migrations.RenameField('rentalitem', 'price', 'price_usd'),
        migrations.AddField(
            model_name='rentalitem',
            name='price_ugx',
            field=models.DecimalField(blank=True, decimal_places=0, help_text='Leave both prices blank for "Price on request".', max_digits=14, null=True, verbose_name='price (UGX)'),
        ),
        migrations.RunPython(move_ugx_prices, migrations.RunPython.noop),
        migrations.RemoveField('rentalitem', 'currency'),
        migrations.AlterField(
            model_name='rentalitem',
            name='price_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='price (US$)'),
        ),
    ]
