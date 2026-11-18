# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Kaizen Safaris: a Django 4.0 marketing/booking site for East African tours (destinations, itineraries, honeymoon spots, equipment hire, gallery), with content managed through the Django admin (Jazzmin theme, CKEditor rich text). Templates are server-rendered and use Tailwind, Alpine.js and GSAP.

## Commands

Python deps are managed with **uv** (`pyproject.toml` / `uv.lock`, Python pinned in `.python-version`). `requirements.txt` lists the same core packages for deployment; `r.txt` is an old, unrelated freeze, so ignore it.

```sh
uv sync                                   # install Python deps into .venv
uv run python manage.py runserver
uv run python manage.py makemigrations && uv run python manage.py migrate
uv run python manage.py test              # all tests (the app tests.py files are mostly empty stubs)
uv run python manage.py test destinations # one app
uv run python manage.py test destinations.tests.SomeTestCase.test_method
uv run python manage.py collectstatic     # needed when DEBUG=False (note: settings use STORAGES, which Django 4.0 ignores, so files aren't hashed)
```

Frontend (run from `static/`; a pnpm lockfile and an npm lockfile both exist):

```sh
pnpm install
pnpm dev      # vite build --watch (rebuilds on src/ and template changes)
pnpm build    # tsc && vite build -> static/public/dist/
```

There is no Vite dev server or HMR: Django serves the built files. Run `pnpm dev` next to `runserver` and reload the browser. The built `static/public/dist/` is committed, so rebuild before committing any frontend or template changes. Templates matter too, because Tailwind only emits the classes it finds in them.

## Configuration

`kaizen/settings.py` reads a `.env` through `django-environ` (`environ.Env.read_env()` looks in the `kaizen/` package dir). `kaizen/.envtemp` is the template. `SECRET_KEY`, `ALLOWED_HOSTS` and all the `EMAIL_*` keys are required, or settings fail to import.

- `DEBUG=True`: SQLite (`db.sqlite3`), with `static/` and `media/` under the project root.
- `DEBUG=False`: the database comes from `DB_*` env vars (read with `os.getenv`, MySQL via `mysqlclient`), and `STATIC_ROOT`/`MEDIA_ROOT` come from env. `passenger_wsgi.py` is gitignored, which suggests deployment on cPanel/Passenger hosting.

## Architecture

The URLs are wired in `kaizen/urls.py` and every app uses a URL namespace (`main:`, `destinations:`, `api:`, `contacts:`), so use namespaced names in `{% url %}` and `reverse`. The custom 404 and 500 handlers live in `main/views.py`.

- **destinations**: the core content model. `Destination` → `Itinerary` (FK `related_name='itineraries'`, has `is_upcoming`, price, dates and a `Duration()` helper) → `Day` (`related_name='days'`). `Itinerary.details` and `Day.description` are CKEditor `RichTextField`s.
- **main**: the home page, gallery, equipment and honeymoon spots. `TopSpot` and `HoneymoonSpot` are FKs to `destinations.Destination`. `HomeView` gathers upcoming tours, featured top spots, honeymoon spots, tours and reviews. It also holds the custom template filters in `main/templatetags/custom_filters.py`.
- **contacts**: plain `forms.Form` classes (`BookingForm`, `TentHireForm`, `CarHireForm`), each with its own `send_mail()` method, which the `FormView`s call from `form_valid`. Mail recipients come from the `Receipient` model (managed in admin). `ContactForm` still has hard-coded addresses. `sendMail` is a DRF `@api_view` used by the footer contact form.
- **api**: small DRF function views for destinations and days. There are no models.
- Enquiry emails for itineraries and honeymoon spots are sent from POST handlers in `destinations/views.py` and `main/views.py`, which render `templates/emails/*.html` with `render_to_string`.

Templates: project-level `templates/` (`base.html`, `components/header.html` / `footer.html`, `404`/`500`, `emails/`) plus per-app `<app>/templates/<app>/`.

### Frontend / static assets

- Django serves static files only from `static/public/` (`STATICFILES_DIRS`). The vendored libraries (lightbox2, swiper) and the images and videos also live under `static/public/`.
- Vite builds `static/src/main.ts` into `static/public/dist/bundle.js` and `bundle.css`, with fonts in `dist/assets/`. `base.html` loads the bundle as `<script type="module">`. `publicDir` is disabled because `public/` is Django's static dir, not Vite's.
- The bundled TS/JS is never rendered by Django, so `{% url %}` and other template tags don't work in `static/src/`. Hard-code the paths or pass values in through the DOM.
- `main.ts` is the entry point: it imports `style.css` and Font Awesome, registers the Alpine plugins (ajax, mask, collapse, anchor, focus) and sets up the GSAP scroll animations driven by the `.fade-in`, `.slide-in-left`, `.slide-in-right` and `.slide-in-top` classes.
- The styling is **Tailwind v4, configured in CSS** (`@theme` in `static/src/style.css`; there's no `tailwind.config.js`). `@source` directives scan the Django templates for classes. Their paths are relative to `static/src/style.css`, and a source must be a file glob (`*/templates/**/*.html`): a bare directory glob matches nothing. The brand tokens are `primary-*`, `grey-*`, `font-body` (Poppins) and `font-lead` (Courgette).
