from django.db import migrations, models


def move_ugx_prices(apps, schema_editor):
    """Prices entered in UGX under the old single-currency fields move to the UGX columns."""
    Itinerary = apps.get_model('tours', 'Itinerary')
    Departure = apps.get_model('tours', 'Departure')
    for tour in Itinerary.objects.exclude(currency='USD'):
        if tour.currency == 'UGX':
            tour.price_from_ugx = tour.price_from_usd
        tour.price_from_usd = None  # EUR/GBP amounts can't be shown any more; re-enter them.
        tour.save(update_fields=['price_from_usd', 'price_from_ugx'])
        for dep in Departure.objects.filter(itinerary=tour, price_usd__isnull=False):
            if tour.currency == 'UGX':
                dep.price_ugx = dep.price_usd
            dep.price_usd = None
            dep.save(update_fields=['price_usd', 'price_ugx'])


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0001_initial'),
    ]

    operations = [
        migrations.RenameField('itinerary', 'price_from', 'price_from_usd'),
        migrations.RenameField('departure', 'price', 'price_usd'),
        migrations.AddField(
            model_name='itinerary',
            name='price_from_ugx',
            field=models.DecimalField(blank=True, decimal_places=0, help_text='Starting price per person in Uganda shillings. Leave both blank to show "Price on request".', max_digits=14, null=True, verbose_name='from (UGX)'),
        ),
        migrations.AddField(
            model_name='departure',
            name='price_ugx',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=14, null=True, verbose_name='price (UGX)'),
        ),
        migrations.RunPython(move_ugx_prices, migrations.RunPython.noop),
        migrations.RemoveField('itinerary', 'currency'),
        migrations.AlterField(
            model_name='itinerary',
            name='price_from_usd',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Starting price per person in US dollars.', max_digits=10, null=True, verbose_name='from (US$)'),
        ),
        migrations.AlterField(
            model_name='departure',
            name='price_usd',
            field=models.DecimalField(blank=True, decimal_places=2, help_text="Per person. Leave both prices blank to use the itinerary's starting prices.", max_digits=10, null=True, verbose_name='price (US$)'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='currency',
            field=models.CharField(choices=[('USD', 'US dollars (US$)'), ('UGX', 'Uganda shillings (UGX)')], default='USD', help_text='Currency of the amounts below (the one the traveller saw when reserving).', max_length=3),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='amount_due',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14),
        ),
    ]
