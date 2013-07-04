# Django settings for alfanousDjango project.


########################################
#     Dynamic or Private settings      #
########################################
from ConfigParser import RawConfigParser


# set the path of your private config file here.
# the file have to be a system-config like, ini-style file, see settings.ini.proto for a prototype
configFile = "./settings.ini.proto" # e,g. '/etc/whatever/settings.ini'

if configFile[:2] == "./":
    print "WARNING: You need to specify a reliable absolute path to the config file, see settings.py"


config = RawConfigParser()
config.read( configFile )

# fetching critical info from the config file
DATABASE_USER = config.get( 'database', 'DATABASE_USER' )
DATABASE_PASSWORD = config.get( 'database', 'DATABASE_PASSWORD' )
DATABASE_HOST = config.get( 'database', 'DATABASE_HOST' )
DATABASE_PORT = config.get( 'database', 'DATABASE_PORT' )
DATABASE_ENGINE = config.get( 'database', 'DATABASE_ENGINE' )
DATABASE_NAME = config.get( 'database', 'DATABASE_NAME' )

MY_DEBUG = config.get( 'debug', 'DEBUG' ) in ["true", "True"]
MY_TEMPLATE_DEBUG = config.get( 'debug', 'TEMPLATE_DEBUG' ) in ["true", "True"]

MY_SECRET_KEY = config.get( 'secrets', 'SECRET_KEY' )

MY_MEDIA_URL = config.get( 'paths', 'MEDIA_URL' )
MY_MEDIA_ROOT = config.get( 'paths', 'MEDIA_ROOT' )

MY_STATIC_URL = config.get( 'paths', 'STATIC_URL' )
MY_STATIC_ROOT = config.get( 'paths', 'STATIC_ROOT' )
MY_STATIC_DIR1 = config.get( 'paths', 'STATIC_DIR1' )

MY_TEMPLATE_DIR1 = config.get( 'paths', 'TEMPLATE_DIR1' )

MY_LOCALE_PATH1 = config.get( 'paths', 'LOCALE_PATH1' )
MY_LOCALE_PATH2 = config.get( 'paths', 'LOCALE_PATH2' )

########################################
#     Static and Public settings       #
########################################

DEBUG = MY_DEBUG
TEMPLATE_DEBUG = MY_TEMPLATE_DEBUG

ADMINS = ( 
     ( 'Assem Chelli', 'assem.ch@gmail.com' ),
 )

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,      # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DATABASE_NAME,          # Or path to database file if using sqlite3.
        'USER': DATABASE_USER,          # Not used with sqlite3.
        'PASSWORD': DATABASE_PASSWORD,  # Not used with sqlite3.
        'HOST': DATABASE_HOST,          # Set to empty string for localhost. Not used with sqlite3.
        'PORT': DATABASE_PORT,          # Set to empty string for default. Not used with sqlite3.
    }
}

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
    ( 'ur', "Urdu" ),
    ( 'ms', "Malay" ),
    ( 'tr', "Turkish" ),
    #( 'sv', "swedish" )
 )


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = MY_MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = MY_MEDIA_URL

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = MY_STATIC_ROOT

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = MY_STATIC_URL

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = ( 
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
MY_STATIC_DIR1,
 )

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = ( 
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
 )

# Make this unique, and don't share it with anybody.
SECRET_KEY = MY_SECRET_KEY


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = ( 
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
 )

MIDDLEWARE_CLASSES = ( 
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
 )

ROOT_URLCONF = 'alfanous-django.urls'

TEMPLATE_DIRS = ( 
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    MY_TEMPLATE_DIR1,
 )

INSTALLED_APPS = ( 
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'alfanous-django.wui',
    # Uncomment the next line to enable the admin:
     'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
 )

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
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


LOCALE_PATHS = ( 
    MY_LOCALE_PATH1,
	MY_LOCALE_PATH2
 )

