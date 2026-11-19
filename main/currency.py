"""Prices in US dollars and Uganda shillings.

Staff enter both amounts in the admin. Visitors see the currency they picked
with the header toggle (a cookie); without one, visitors in Uganda see UGX and
everyone else sees USD.
"""
import ipaddress
from bisect import bisect_right
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from django.db import models

COOKIE = 'currency'
DEFAULT = 'USD'
HOME = 'UGX'  # shown by default to visitors in Uganda
UGANDA_IPS = Path(__file__).resolve().parent / 'data' / 'uganda_ips.txt'


class Currency(models.TextChoices):
    USD = 'USD', 'US dollars (US$)'
    UGX = 'UGX', 'Uganda shillings (UGX)'


SYMBOLS = {'USD': 'US$', 'UGX': 'UGX '}


def format_money(value, currency=DEFAULT):
    """2850 -> "US$2,850". Blank prices read "Price on request"."""
    if value in (None, ''):
        return 'Price on request'
    value = Decimal(value)
    fmt = '{:,.0f}' if value == value.to_integral() or currency == 'UGX' else '{:,.2f}'
    return f'{SYMBOLS.get(currency, currency + " ")}{fmt.format(value)}'


class Prices:
    """One price in both currencies; either amount may be missing."""

    def __init__(self, usd=None, ugx=None):
        self.amounts = {'USD': usd, 'UGX': ugx}

    def __bool__(self):
        return any(v is not None for v in self.amounts.values())

    def __str__(self):
        return ' / '.join(format_money(v, c) for c, v in self.items()) or 'Price on request'

    def items(self):
        return [(c, v) for c, v in self.amounts.items() if v is not None]

    def pick(self, currency):
        """(amount, currency) in the wanted currency, else whichever is filled in."""
        if self.amounts.get(currency) is not None:
            return self.amounts[currency], currency
        for c, v in self.items():
            return v, c
        return None, currency


# --- Visitor location -------------------------------------------------------

@lru_cache(maxsize=1)
def _uganda_ranges():
    """Sorted (first, last) integer ranges per IP version, from the AFRINIC registry."""
    ranges = {4: [], 6: []}
    try:
        lines = UGANDA_IPS.read_text().splitlines()
    except FileNotFoundError:
        lines = []
    for line in lines:
        line = line.split('#')[0].strip()
        if not line:
            continue
        first, last = (ipaddress.ip_address(p) for p in line.split())
        ranges[first.version].append((int(first), int(last)))
    for v in ranges:
        ranges[v].sort()
    return {v: (r, [a for a, _ in r]) for v, r in ranges.items()}


def ip_in_uganda(ip):
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    ranges, starts = _uganda_ranges()[addr.version]
    i = bisect_right(starts, int(addr)) - 1
    return i >= 0 and int(addr) <= ranges[i][1]


def client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return forwarded.split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')


def visitor_in_uganda(request):
    # Cloudflare (if the site is ever put behind it) tells us the country directly.
    country = request.META.get('HTTP_CF_IPCOUNTRY')
    if country and country not in ('XX', 'T1'):
        return country.upper() == 'UG'
    return ip_in_uganda(client_ip(request))


def currency_for(request):
    chosen = request.COOKIES.get(COOKIE)
    if chosen in Currency.values:
        return chosen
    return HOME if visitor_in_uganda(request) else DEFAULT
