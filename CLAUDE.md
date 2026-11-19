# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Kaizen Safaris (canonical URL https://kaizen-safaris.com): a Django 4.0 / Python 3.9 site for an East African tour operator. It covers tours (day-by-day and flexible itineraries with scheduled group departures and seat reservations), destinations and places, a blog, rentals, and enquiry forms. All content is managed in the Django admin (Jazzmin theme, CKEditor). Templates are server-rendered with Tailwind v4, Alpine.js and GSAP.

Stay on Django 4.0 (the owner decided against upgrading). Don't use 4.1+ APIs: for example, the `STORAGES` setting is ignored, so set `STATICFILES_STORAGE` instead.

## Commands

Python deps are managed with **uv** (`pyproject.toml` / `uv.lock`). `requirements.txt` mirrors them for deployment.

```sh
uv sync
uv run python manage.py runserver
uv run python manage.py migrate
uv run python manage.py seed_demo [--flush]   # sample content for local dev (refuses when DEBUG=False)
uv run python manage.py test                  # all tests
uv run python manage.py test tours            # one app
uv run python manage.py test tours.tests.ReservationFlowTests.test_cannot_exceed_seats
uv run python manage.py collectstatic         # production; uses whitenoise manifest (hashed) storage
```

Frontend (run from `static/`, with pnpm):

```sh
pnpm install
pnpm dev      # vite build --watch (rebuilds on src/ and template changes)
pnpm build    # tsc && vite build -> static/public/dist/
```

There is no Vite dev server or HMR: Django serves the built files. Run `pnpm dev` next to `runserver` and reload the browser. The built `static/public/dist/` is committed, so rebuild before committing any frontend or template change. Templates matter too, because Tailwind only emits the classes it finds in them.

## Configuration

`kaizen/settings.py` reads `kaizen/.env` through `django-environ`, using `kaizen/.envtemp` as the template. `SECRET_KEY` and `ALLOWED_HOSTS` are required. `SITE_URL` (default `https://kaizen-safaris.com`) drives canonical links, the sitemap and the JSON-LD. Email settings are optional: without them mail goes to the console backend.

- `DEBUG=True`: SQLite at `db.sqlite3`, with `staticfiles/` and `media/` under the project root.
- `DEBUG=False`: the database comes from `DB_*` env vars (MySQL), `STATIC_ROOT`/`MEDIA_ROOT` come from env, and whitenoise serves hashed static files. Deployment is cPanel/Passenger (`passenger_wsgi.py` is gitignored).

## Architecture

Each app has a URL namespace (`main`, `destinations`, `tours`, `rentals`, `blog`, `contacts`). Public URLs use slugs.

- **`main/mixins.py`**: the abstract bases every content model builds on. `Page` = timestamps + an auto-generated unique `slug` (from `slug_source`) + SEO fields (`meta_title`/`meta_description`) + `is_published` + `OptimisedImages`, which downscales newly uploaded files listed in `image_fields`. Public querysets filter with `.published()`.
- **destinations**: `Destination` (country) → `Place` (park, lake, beach…) with a `PlaceImage` gallery. `TripStyle` (Honeymoon, Gorilla trekking…) tags both places and itineraries. Honeymoons are a trip style, not a separate model.
- **tours**: `Itinerary.format` is either `day_by_day` (content in `Day` rows, which can span `day_from`–`day_to`) or `flexible` (content in `overview` + highlight `places`). Both formats can have `Departure`s (scheduled dates with `seats_total`). A `Reservation` holds seats while its status is in `HOLDING_STATUSES`. Payment is collected offline and tracked by staff in the admin (`amount_due`/`amount_paid`). Use `Departure.objects.with_seats()` to annotate seat counts in lists, and `is_bookable` for the booking rules. `reserve()` locks the departure row while checking seats. The confirmation page is visible only to the browser session that made the reservation.
- **contacts**: every form (contact, trip planner, itinerary quote, rental) subclasses `EnquiryForm` and is saved as an `Enquiry`. Fields not in `core_fields` go into `Enquiry.details` (JSON). Forms carry a honeypot `website` field. `contacts/notify.py` emails the active `Recipient`s (falling back to the SiteSettings email); send failures are logged, never shown to visitors.
- **Currency** (`main/currency.py`): every price is entered twice in the admin, in USD and UGX (`price_from_usd`/`price_from_ugx`, `price_usd`/`price_ugx`); models expose them as a `Prices` object (`itinerary.price_from`, `departure.effective_price`, `rental_item.price`). `CurrencyMiddleware` sets `request.currency`: the header toggle's `currency` cookie first, otherwise UGX for visitors in Uganda (Cloudflare `CF-IPCountry` if present, else the AFRINIC ranges in `main/data/uganda_ips.txt`, refreshed with `manage.py update_uganda_ips`) and USD for everyone else. Render prices with `{% price obj.price_from %}`, which falls back to the other currency when one is blank. A `Reservation` stores the `currency` its amounts are in.
- **blog**: `Post` (draft/published, with `published_at` scheduling) with `Author`, `Category` and `Tag`, plus M2M links to destinations, places and itineraries. These render as "Plan this trip" cards.
- **rentals**: `RentalCategory` → `RentalItem` on one page with a `RentalForm` enquiry.
- **main**: `SiteSettings` is a singleton (`SiteSettings.load()`) holding contact details, socials and the payment instructions shown after a reservation. The context processor `main.context_processors.site` exposes `site`, nav destinations/styles and the organisation JSON-LD to every template. Also here: `Review`, `Photo`, `Video`, home, gallery, robots.txt, humans.txt and error views.

### SEO

- `base.html` blocks: `title`, `meta_description`, `canonical`, `og_*`, `extra_meta` and `structured_data`. A view sets `noindex` in its context to emit robots noindex. That's done for filtered or searched listings, tag pages, reservation and thank-you pages.
- Views pass `breadcrumbs` as a list of `(label, url_or_None)`. It's rendered visually and as BreadcrumbList JSON-LD.
- `main/seo.py` builds the JSON-LD (TravelAgency + WebSite, TouristTrip with Offers per departure, TouristAttraction, TouristDestination, BlogPosting). Render it with the `jsonld` filter from `{% load kaizen %}`. The same library provides `price`, `money`, `absolute`, `field` (form-field markup), `page_url` and `stars`.
- `main/sitemaps.py` always emits `SITE_URL` URLs, whatever host the request came in on.
- The developer credit (DakdotCreations Limited, dakdot.com) is deliberately hidden: an HTML comment, `meta name="designer"`, humans.txt and WebSite `creator` in the JSON-LD. Never add a visible "developed by" line; a test enforces this.

### Frontend

- Django serves static files only from `static/public/`. Vite builds `static/src/main.ts` into `static/public/dist/bundle.{js,css}` (fonts in `dist/assets/`), loaded as `<script type="module">`.
- Bundled TS is never rendered by Django, so template tags don't work in `static/src/`. Pass values through the DOM or `x-data`.
- `main.ts` registers Alpine components: `siteHeader` (transparent over a hero, solid once scrolled), `lightbox` (reads `[data-lightbox]` children) and `rail` (prev/next for `.rail` scrollers). It also runs the GSAP reveal animations for `.fade-in` / `.slide-in-*`, with an optional `data-delay`. Reveal styles only apply once `html.js` is set, so content stays visible if JS fails.
- Pages with a full-bleed hero include the header with `overlay=True` (`{% block header %}`) and use `components/page_hero.html`.
- Tailwind v4 is configured in CSS (`@theme` in `static/src/style.css`, no `tailwind.config.js`). Component classes such as `btn`, `card`, `field`, `prose`, `kicker` and `section-title` are defined there. `@source` paths are relative to `style.css` and must be file globs. `group` can't be `@apply`'d; put it in the markup.
