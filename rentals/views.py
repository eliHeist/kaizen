from django.db.models import Prefetch
from django.shortcuts import redirect, render

from contacts import notify
from contacts.forms import RentalForm
from rentals.models import RentalCategory, RentalItem


def rentals(request):
    initial = {}
    if request.GET.get('item', '').isdigit():
        initial['items'] = [int(request.GET['item'])]
    form = RentalForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        notify.enquiry_received(form.save(request))
        return redirect('contacts:thanks')

    categories = RentalCategory.objects.prefetch_related(
        Prefetch('items', queryset=RentalItem.objects.filter(is_available=True))
    )
    return render(request, 'rentals/rentals.html', {
        'categories': [c for c in categories if c.items.all()],
        'form': form,
        'breadcrumbs': [('Rentals', None)],
    })
