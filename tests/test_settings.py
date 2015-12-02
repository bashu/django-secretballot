import os
SECRET_KEY = 'tests'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'secretballot',
    'tests',
)

TEMPLATE_DIRS = (os.path.dirname(__file__),)

MIDDLEWARE_CLASSES = ()
