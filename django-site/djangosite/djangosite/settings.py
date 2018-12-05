"""
Django settings for djangosite project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os
import json


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

configuracao_path = os.path.join(BASE_DIR, 'config.json')
if os.path.exists(configuracao_path):
    with open(configuracao_path) as arquivo:
        configuracao = json.load(arquivo)
else:
    raise ValueError('Arquivo de configuração "config.json" não existente!')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = configuracao['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = configuracao['DEBUG']

ALLOWED_HOSTS = configuracao['ALLOWED_HOSTS']

# Application definition

INSTALLED_APPS = [
    # Padrão
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Para ediçao de páginas estáticas (requer o comando 'collectstatic' do
    # django)
    'ckeditor',
    'ckeditor_uploader',

    # Nossos aplicativos
    'paginas_estaticas',
    'ouvidoria',
    'noticias',
    'atas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djangosite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangosite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgresql',
        'USER': 'postgresql',
        'PASSWORD': 'postgresql',
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

APPEND_SLASH = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_URL = '/static/'

# Para o comando 'collectstatic'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Arquivos estáticos a serem servidos
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "djangosite/static/"),
]

# Configurações do CKEditor
CKEDITOR_CONFIGS = {
    'default': {
        'extraPlugins': 'sourcedialog,',
        'removePlugins': 'sourcearea,',
        'toolbar': 'full',
    }
}

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'
CKEDITOR_UPLOAD_PATH = 'uploaded/'

# Dados para captcha (página de contatos e membros)
CAPTCHA_SITE_KEY = configuracao['CAPTCHA_SITE_KEY']
CAPTCHA_SECRET_KEY = configuracao['CAPTCHA_SECRET_KEY']

# Configurações de e-mail para página de contato
EMAIL_HOST = configuracao['EMAIL_HOST']
EMAIL_PORT = configuracao['EMAIL_PORT']
EMAIL_HOST_USER = configuracao['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = configuracao['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = configuracao['EMAIL_USE_TLS']
EMAIL_USE_SSL = configuracao['EMAIL_USE_SSL']
# Qual o e-mail que aparecerá como remetente
EMAIL_CONTATO_REMETENTE = configuracao['EMAIL_CONTATO_REMETENTE']
# Qual o(s) destinatário(s) para os e-mails da ouvidoria (página '/contato/')
EMAIL_CONTATO_DESTINATARIO = configuracao['EMAIL_CONTATO_DESTINATARIO']
# Qual o e-mail que aparecerá na página de contato em caso de falha
EMAIL_CONTATO_DISPLAY = configuracao['EMAIL_CONTATO_DISPLAY']

# Notícias por página no site
NOTICIAS_POR_PAGINA = 5
NOTICIAS_POR_PAGINA_RAIZ = 3

# Atas por página no site
ATAS_BARRA_LATERAL = 3
ATAS_POR_PAGINA = 3
ATAS_REUNIAO_POR_PAGINA = 7
ATAS_ASSEMBLEIA_POR_PAGINA = 7
