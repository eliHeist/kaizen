from django.utils.cache import patch_vary_headers

from main.currency import currency_for


class CurrencyMiddleware:
    """Sets ``request.currency`` (USD or UGX) for showing prices."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.currency = currency_for(request)
        response = self.get_response(request)
        patch_vary_headers(response, ('Cookie',))
        return response
