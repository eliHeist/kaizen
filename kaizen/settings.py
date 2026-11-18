import os
from pathlib import Path

import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env()  # reads kaizen/.env (see kaizen/.envtemp)

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Canonical public URL, used for canonical links, the sitemap and structured data.
SITE_URL = env('SITE_URL', default='https://kaizen-safaris.com').rstrip('/')
CSRF_TRUSTED_ORIGINS = [SITE_URL]

# Search console ownership tokens (the content="" value of the meta tag each tool gives you).
GOOGLE_SITE_VERIFICATION = env('GOOGLE_SITE_VERIFICATION', default='')
BING_SITE_VERIFICATION = env('BING_SITE_VERIFICATION', default='')

if not DEBUG:
    # cPanel/Passenger terminates TLS in front of Django.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
    SESSION_COOKIE_SECURE = env.bool('SECURE_COOKIES', default=True)
    CSRF_COOKIE_SECURE = env.bool('SECURE_COOKIES', default=True)
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.humanize',

    'crispy_forms',
    'crispy_tailwind',
    'ckeditor',
    'ckeditor_uploader',

    'main',
    'destinations',
    'tours',
    'rentals',
    'blog',
    'contacts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kaizen.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.site',
            ],
        },
    },
]

WSGI_APPLICATION = 'kaizen.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('DB_ENGINE'),
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            # uncomment below for mysql
            # 'OPTIONS': {
            #     'init_command': "SET sql_mode='STRICT_TRANS_TABLES', innodb_strict_mode=1",
            #     'charset': 'utf8mb4',
            # },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Africa/Kampala'
USE_I18N = True
USE_TZ = True


# Static and media files

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [BASE_DIR / 'static' / 'public']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, str(env('STATIC_ROOT')))
    MEDIA_ROOT = os.path.join(BASE_DIR, str(env('MEDIA_ROOT')))
    # Hashed filenames so browsers can cache bundle.js/bundle.css forever and
    # still pick up each new build. (Django 4.0 reads this, not STORAGES.)
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'tailwind'
CRISPY_TEMPLATE_PACK = 'tailwind'


# Email. Without settings, messages are printed to the console (handy in development).

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend') or \
    'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='') or EMAIL_HOST_USER or 'webmaster@localhost'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'WARNING'},
}


# Rich text editor

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_RESTRICT_BY_DATE = True
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Format', 'Bold', 'Italic', 'Underline', 'Strike'],
            ['NumberedList', 'BulletedList', 'Blockquote', '-', 'Outdent', 'Indent'],
            ['Link', 'Unlink', 'Image', 'Table', 'HorizontalRule'],
            ['RemoveFormat', 'Source', 'Maximize'],
        ],
        'format_tags': 'p;h2;h3;h4',
        'height': 320,
        'width': '100%',
    },
}


# Admin theme

JAZZMIN_SETTINGS = {
    'site_title': 'Kaizen Safaris',
    'site_header': 'Kaizen Safaris',
    'site_brand': 'Kaizen Safaris',
    'site_logo': 'img/logo.webp',
    'login_logo': 'img/logo.webp',
    'login_logo_dark': 'img/logo.webp',
    'site_logo_classes': 'img-circle',
    'site_icon': 'img/logo.webp',
    'welcome_sign': 'Welcome to the Admin Center',
    'copyright': 'DakdotCreations Limited',
    'search_model': ['tours.Itinerary', 'tours.Reservation', 'blog.Post', 'destinations.Place'],
    'topmenu_links': [
        {'name': 'Home', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        {'name': 'View site', 'url': 'main:home', 'new_window': True},
        {'model': 'tours.Reservation'},
        {'model': 'contacts.Enquiry'},
    ],
    'show_sidebar': True,
    'navigation_expanded': True,
    'order_with_respect_to': [
        'tours', 'tours.Reservation', 'tours.Departure', 'tours.Itinerary',
        'contacts', 'destinations', 'blog', 'rentals', 'main', 'auth',
    ],
    'icons': {
        'auth': 'fas fa-users-cog',
        'auth.user': 'fas fa-user',
        'auth.Group': 'fas fa-users',
        'tours.Itinerary': 'fas fa-route',
        'tours.Departure': 'fas fa-calendar-alt',
        'tours.Reservation': 'fas fa-ticket-alt',
        'destinations.Destination': 'fas fa-globe-africa',
        'destinations.Place': 'fas fa-map-marker-alt',
        'destinations.TripStyle': 'fas fa-tags',
        'blog.Post': 'fas fa-newspaper',
        'blog.Author': 'fas fa-user-edit',
        'blog.Category': 'fas fa-folder',
        'blog.Tag': 'fas fa-hashtag',
        'rentals.RentalCategory': 'fas fa-boxes',
        'rentals.RentalItem': 'fas fa-car',
        'contacts.Enquiry': 'fas fa-inbox',
        'contacts.Recipient': 'fas fa-at',
        'main.SiteSettings': 'fas fa-cog',
        'main.Review': 'fas fa-star',
        'main.Photo': 'fas fa-images',
        'main.Video': 'fab fa-youtube',
    },
    'default_icon_parents': 'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-circle',
    'related_modal_active': False,
    'use_google_fonts_cdn': True,
    'show_ui_builder': False,
    'changeform_format': 'horizontal_tabs',
    'changeform_format_overrides': {'auth.user': 'collapsible', 'auth.group': 'vertical_tabs'},
}
