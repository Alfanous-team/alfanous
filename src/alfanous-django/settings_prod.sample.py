DEBUG = False
TEMPLATE_DEBUG = False

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'alfanous-django',
    'USER': 'root',
    'PASSWORD': 'root',
  }
}

EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
EMAIL_USE_TLS = True

MEDIA_ROOT = ''
