# -*- coding: utf-8 -*-

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "DUMMY_SECRET_KEY"

INTERNAL_IPS = []

# Application definition

PROJECT_APPS = ["secretballot.tests", "secretballot"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
] + PROJECT_APPS

MIDDLEWARE = []

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "tests", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

SECRETBALLOT_FOR_MODELS = {
    "tests.Link": {},
    "tests.WeirdLink": {
        "votes_name": "vs",
        "upvotes_name": "total_upvs",
        "downvotes_name": "total_downvs",
        "total_name": "v_total",
        "add_vote_name": "add_v",
        "remove_vote_name": "remove_v",
    },
    "tests.AnotherLink": {
        "manager_name": "ballot_custom_manager",
    },
}
