#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    openslides.openslides_settings
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    OpenSlides default settings.

    :copyright: 2011, 2012 by OpenSlides team, see AUTHORS.
    :license: GNU GPL, see LICENSE for more details.
"""

import os
import sys
from django.conf.global_settings import *

_fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
def _fs2unicode(s):
    if isinstance(s, unicode):
        return s
    return s.decode(_fs_encoding)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
#SITE_ROOT = os.path.join(SITE_ROOT, '..')


AUTH_PROFILE_MODULE = 'participant.Profile'
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', 'openslides.utils.auth.AnonymousAuth',)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

DBPATH = _fs2unicode(os.path.join(os.path.join(SITE_ROOT, '..'), 'database.db'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DBPATH,                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


ugettext = lambda s: s

LANGUAGES = (
    ('de', ugettext('German')),
    ('en', ugettext('English')),
)


# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(SITE_ROOT, './static/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory that holds static media from ``collectstatic``
# Example: "/home/media/static.lawrence.com/"
STATIC_ROOT = _fs2unicode(os.path.join(SITE_ROOT, '../site-static'))

# URL that handles the media served from STATIC_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://static.lawrence.com", "http://example.com/static/"
STATIC_URL  = '/static/'

# Additional directories containing static files (not application specific)
# Examples: "/home/media/lawrence.com/extra-static/"
STATICFILES_DIRS = (
    _fs2unicode(os.path.join(SITE_ROOT, 'static')),
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'openslides.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    _fs2unicode(os.path.join(SITE_ROOT, 'templates')),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mptt',
    'utils',
    'poll',
    'projector',
    'agenda',
    'application',
    'assignment',
    'participant',
    'config',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
    'utils.utils.revision',
    'openslides.utils.auth.anonymous_context_additions',
)
