from pathlib import Path
from dotenv import load_dotenv
import os

# ===============================
# LOAD ENV VARIABLES
# ===============================
load_dotenv()

# ===============================
# BASE DIR
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent

# ===============================
# BLOCKCHAIN CONFIG
# ===============================
ALCHEMY_POLYGON_AMOY = os.getenv("ALCHEMY_POLYGON_AMOY")

OWNER_PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY")
VALIDATOR_PRIVATE_KEY = os.getenv("VALIDATOR_PRIVATE_KEY")
BENEFICIARY_PRIVATE_KEY = os.getenv("BENEFICIARY_PRIVATE_KEY")

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")
import os

CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS")

# ===============================
# SECURITY
# ===============================
SECRET_KEY = 'django-insecure-__p4r=mm7+05!1m-9r1(#cv)geb$t31-+g1scg24^#+2iv*$i@'

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ===============================
# CSRF & SESSION CONFIG
# ===============================
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False   # Set True in production (HTTPS)
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8000"]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = False

# ===============================
# APPLICATIONS
# ===============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dashboard',
]

# ===============================
# MIDDLEWARE
# ===============================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # IMPORTANT
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ===============================
# URL CONFIG
# ===============================
ROOT_URLCONF = 'digital_will.urls'

# ===============================
# TEMPLATES
# ===============================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # optional global templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # REQUIRED
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'digital_will.wsgi.application'

# ===============================
# DATABASE
# ===============================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ===============================
# PASSWORD VALIDATION
# ===============================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

# ===============================
# INTERNATIONALIZATION
# ===============================
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

# ===============================
# STATIC FILES
# ===============================
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "dashboard" / "static"
]

# ===============================
# MEDIA FILES
# ===============================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===============================
# DEFAULT FIELD
# ===============================
