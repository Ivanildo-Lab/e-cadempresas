

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Env primeiro (Coolify); fallback = chave antiga (repo privado). PENDENTE: rotacionar pos-migracao.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-a3vs_q@2lx%obo*zks3^!6^b&-t1r$^6fgda%tly2du83*cd=x',
)

# SECURITY WARNING: don't run with debug turned on in production!
# DJANGO_DEBUG no Coolify; padrao False (nunca mais DEBUG=True hardcoded).
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() in ('1', 'true', 'yes')


def _csv(value):
    """Divide uma env CSV em lista, removendo espacos das pontas."""
    return [v.strip() for v in value.split(',') if v.strip()]


# Fallback cobre VPS/domínios novos + PA (legado) + 0.0.0.0 (healthcheck do Traefik)
ALLOWED_HOSTS = _csv(
    os.environ.get(
        'DJANGO_ALLOWED_HOSTS',
        'ecadempresas.ivcsofthouse.com.br,ecadempresas.187-127-63-185.sslip.io,'
        'ecadempresas-geficogestor.pythonanywhere.com,geficogestor.pythonanywhere.com,'
        '0.0.0.0,localhost,127.0.0.1',
    )
)

CSRF_TRUSTED_ORIGINS = _csv(
    os.environ.get(
        'DJANGO_CSRF_TRUSTED_ORIGINS',
        'https://ecadempresas.ivcsofthouse.com.br,https://ecadempresas.187-127-63-185.sslip.io,'
        'http://ecadempresas-geficogestor.pythonanywhere.com,http://geficogestor.pythonanywhere.com',
    )
)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
       'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    # Caminho absoluto a partir do BASE_DIR: o banco é sempre o mesmo
    # independente do CWD (era a causa do "no such column" local).
    # Sem dj_database_url de propósito: o venv de produção não tem
    # essa dependência e o sqlite local não precisa dela.
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # SQLITE_PATH aponta para o VOLUME (/app/data/db.sqlite3) no Docker;
        # sem env, mantem o comportamento legado (BASE_DIR/db.sqlite3) no PA/local.
        'NAME': os.environ.get('SQLITE_PATH', str(BASE_DIR / 'db.sqlite3')),
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root') # Pasta onde o Django vai reunir tudo para produção
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
# STORAGES (Django 4.2+; STATICFILES_STORAGE foi descontinuado)
# Compressed SEM manifest — collectstatic nunca falha por source map ausente
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}

# Proxy SSL (Traefik/HTTPS)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'