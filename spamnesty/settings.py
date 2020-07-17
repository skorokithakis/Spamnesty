import os
import re
from subprocess import check_output  # noqa
from typing import Dict
from typing import Union

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "secret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get("NODEBUG") is None else False

ALLOWED_HOSTS = (
    ["web", "localhost"] if os.environ.get("NODEBUG") is None else [".mnesty.com"]
)

DEFAULT_FROM_EMAIL = "Spamnesty <noreply-sp@mnesty.com>"


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "raven.contrib.django.raven_compat",
    "django_extensions",
    "django_nose",
    "bootstrap3",
    "main",
    "classification",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "spamnesty.stats_middleware.StatsMiddleware",
    "raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

NOSE_ARGS = ["--nocapture", "--nologcapture", "--stop"]
NOSE_ARGS += [
    "--cover-package=spamnesty",
    "--cover-package=main",
    "--cover-erase",
    "--cover-html",
    "--cover-html-dir=htmlcov",
]
NOSE_ARGS += ["--with-coverage"]

ROOT_URLCONF = "spamnesty.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "spamnesty.context_processors.settings",
            ]
        },
    }
]

WSGI_APPLICATION = "spamnesty.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

if os.environ.get("IN_DOCKER"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.environ.get("DB_NAME", "spamnesty"),
            "USER": os.environ.get("DB_USER", "spamnesty"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", ""),
            "PORT": os.environ.get("DB_PORT", 5432),
        }
    }
elif os.environ.get("DATABASE_URL"):
    # Stuff for when running in Dokku.

    # Parse the DATABASE_URL env var.
    USER, PASSWORD, HOST, PORT, NAME = re.match(  # type: ignore
        r"^postgres://(?P<username>.*?)\:(?P<password>.*?)\@(?P<host>.*?)\:(?P<port>\d+)\/(?P<db>.*?)$",
        os.environ.get("DATABASE_URL", ""),
    ).groups()

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": NAME,
            "USER": USER,
            "PASSWORD": PASSWORD,
            "HOST": HOST,
            "PORT": int(PORT),
        }
    }

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv("REDIS_URL", ""),
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
    SESSION_COOKIE_AGE = 365 * 24 * 60 * 60
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


try:
    COMMIT_HASH = check_output(["git", "rev-parse", "--short", "HEAD"]).strip()
except:  # noqa
    COMMIT_HASH = "Not a git repo"


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = False

USE_L10N = False

USE_TZ = False

SITE_ID = 1

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        }
    },
}


EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.elasticemail.com"
EMAIL_HOST_USER = "elasticemail@mail.stavros.io"
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
EMAIL_PORT = 2525


RAVEN_CONFIG: Dict[str, Union[None, str]] = {"dsn": os.environ.get("RAVEN_DSN")}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "_static")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

try:
    from .local_settings import *  # noqa
except ImportError:
    pass

try:
    INSTALLED_APPS += LOCAL_INSTALLED_APPS  # type: ignore # noqa
except:  # noqa
    pass

try:
    MIDDLEWARE_CLASSES += LOCAL_MIDDLEWARE_CLASSES  # type: ignore # noqa
except:  # noqa
    pass
