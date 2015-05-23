SECRET_KEY = 'tests'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'secretballot',
    'tests',
)

MIDDLEWARE_CLASSES = ()
