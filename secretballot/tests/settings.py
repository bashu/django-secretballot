SECRET_KEY = "DUMMY_SECRET_KEY"  # noqa: S105

# Application definition

PROJECT_APPS = ["secretballot.tests", "secretballot"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    *PROJECT_APPS,
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
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
