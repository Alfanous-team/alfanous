# Django settings for alfanousDjango project.
import os
from collections import OrderedDict as SortedDict
from django.utils.translation import ugettext_lazy as _

# the root directory of alfanous-django
ROOT_DIR = os.path.dirname(__file__)


########################################
#     Static and Public settings       #
########################################

DEBUG = True

INSTALLED_APPS = (
  # Django apps
  'django.contrib.admin',
  'django.contrib.admindocs',
  # 'suit',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.sites',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  # 'rest_framework',
  # 'dynamic_rest',
  # 'rest_framework.authtoken',
  # 3rd party apps
  'debug_toolbar',
  'template_timings_panel',

  # our apps
  'wui',
  "compressor",
)



ADMINS = (
  ( 'Assem Chelli', 'assem.ch@gmail.com' ),
  ( 'Mouad Debbar', 'mouad.debbar@gmail.com' ),
)

MANAGERS = ADMINS

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'main.db',
  }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Africa/Algiers'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = (
  ( 'ar', "Arabic" ),
  ( 'en', "English" ),
  ( 'fr', "French" ),
  ( 'id', "Indonesian" ),
  ( 'ja', "Japanese"),
  ( 'ku', "Kurdish" ),
  #( 'ur', "Urdu" ),
  ( 'ms', "Malay" ),
  ( 'ml', "Malayalam" ),
  ( 'tr', "Turkish" ),
  ( 'es', "Spanish" ),
  ( 'pt', "Portuguese"),
  #( 'sv', "swedish" )
)

# These are languages not supported by Django core. We have to provide
# their info here so we can use them in our templates. This is mainly
# used in `wui.templatetags.languages`.
EXTRA_LANGUAGES = {
  'ku': {
    'code': 'ku',
    'name': 'Kurdish',
    'bidi': True,
    'name_local': 'Kurdish'
  },
  'ms': {
    'code': 'ms',
    'name': 'Malay',
    'bidi': False,
    'name_local': 'Malay'
  },
}


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(ROOT_DIR, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(ROOT_DIR, 'static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
  # Put strings here, like "/home/html/static" or "C:/www/django/static".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
  # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
  'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'kl2wmaaul8-roi3k9*@1j9kse%z^durtud=8l-*6+r#h2mo*80'


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'alfanous-django/templates')],

        'APP_DIRS': True,
      'OPTIONS': {
        'context_processors': [
          'django.template.context_processors.request',
          'django.contrib.auth.context_processors.auth',
          'django.contrib.messages.context_processors.messages',
        ],
      },
    },
]

MIDDLEWARE_CLASSES = (
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.locale.LocaleMiddleware',
  'debug_toolbar.middleware.DebugToolbarMiddleware',
  'htmlmin.middleware.HtmlMinifyMiddleware',
  'htmlmin.middleware.MarkRequestMiddleware',
)

ROOT_URLCONF = 'urls'


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'filters': {
    'require_debug_false': {
      '()': 'django.utils.log.RequireDebugFalse'
    }
  },
  'handlers': {
    'mail_admins': {
      'level': 'ERROR',
      'filters': ['require_debug_false'],
      'class': 'django.utils.log.AdminEmailHandler'
    }
  },
  'loggers': {
    'django.request': {
      'handlers': ['mail_admins'],
      'level': 'ERROR',
      'propagate': True,
      },
    }
}

# default
DEBUG_TOOLBAR_PANELS = (
  'debug_toolbar.panels.versions.VersionsPanel',
  'debug_toolbar.panels.timer.TimerPanel',
  'debug_toolbar.panels.settings.SettingsPanel',
  'debug_toolbar.panels.headers.HeadersPanel',
  'debug_toolbar.panels.request.RequestPanel',
  'debug_toolbar.panels.sql.SQLPanel',
  'debug_toolbar.panels.staticfiles.StaticFilesPanel',
  'debug_toolbar.panels.templates.TemplatesPanel',
  # 'debug_toolbar.panels.cache.CachePanel',
  # 'debug_toolbar.panels.signals.SignalsPanel',
  # 'debug_toolbar.panels.logging.LoggingPanel',
  'debug_toolbar.panels.redirects.RedirectsPanel',
)

# added by @mdebbar
DEBUG_TOOLBAR_PANELS += (
  'template_timings_panel.panels.TemplateTimings.TemplateTimings',
)


LOCALE_PATHS = (
  os.path.join(ROOT_DIR, 'locale/'),
)

# We are using lazy translation, so these strings will be translated in the
# template not here.
AVAILABLE_UNITS = SortedDict([
  ( "aya", _("Ayahs") ),
  #( "sura", "Surahs" ),

  ( "translation", _("Translations") ),
  # ( "word", _("Words") ),
  #  tafsir, hadith, dream, poem
])

HTML_MINIFY = True

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = False
COMPRESS_STORAGE = 'compressor.storage.GzipCompressorFileStorage'
GZIP_CONTENT_TYPES = (
    'text/css',
    'application/javascript',
    'application/x-javascript',
    'text/javascript'
)

################################
#     Production settings      #
################################
## Keep this part at the end of this file
try:
  # load production settings if there is any
  from settings_prod import *
except ImportError:
  # There are no prod settings
  pass
