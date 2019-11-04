import os


COMPANY_NAME = os.environ['COMPANY_NAME']
COMPANY_NICKNAME = os.environ.get('COMPANY_NICKNAME', COMPANY_NAME)
COMPANY_SITE = os.environ.get('COMPANY_SITE')

GOOGLE_DRIVE_API_KEY = os.environ['GOOGLE_DRIVE_API_KEY']

PREMIER_BASE_URL = 'https://api.premierwd.com/api/v5'
PREMIER_API_KEY = os.environ['PREMIER_API_KEY']

SEMA_BASE_URL = 'https://sdc.semadatacoop.org/sdcapi'
SEMA_USERNAME = os.environ['SEMA_USERNAME']
SEMA_PASSWORD = os.environ['SEMA_PASSWORD']


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.environ['SECRET_KEY']


DEBUG = True
ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreAppConfig',
    'main.apps.MainAppConfig',
    'premier.apps.PremierAppConfig',
    'sema.apps.SemaAppConfig',
    'shopify.apps.ShopifyAppConfig',
    'admin_reorder',
    'import_export',
    'imagekit'
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder'
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'core', 'templates'),
            os.path.join(BASE_DIR, 'main', 'templates'),
            os.path.join(BASE_DIR, 'premier', 'templates'),
            os.path.join(BASE_DIR, 'sema', 'templates'),
            os.path.join(BASE_DIR, 'shopify', 'templates')
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
            'loaders': [
                (
                    'django.template.loaders.cached.Loader', [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader'
                    ]
                ),
            ]
        }
    }
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '')
    },
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': os.environ['DATABASE_NAME'] + '_test',
    #     'USER': os.environ['DATABASE_USER'],
    #     'PASSWORD': os.environ['DATABASE_PASSWORD'],
    #     'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
    #     'PORT': os.environ.get('DATABASE_PORT', '')
    # }
}
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        )
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        )
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        )
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        )
    }
]


ROOT_URLCONF = 'ecommercejockey.urls'
WSGI_APPLICATION = 'ecommercejockey.wsgi.application'

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'


TIMEOUT = None
DATA_UPLOAD_MAX_NUMBER_FIELDS = None


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


ADMIN_REORDER = (
    {
        'app': 'auth',
        'label': 'Authorization',
        'models': (
            'auth.User',
            'auth.Group'
        )
    },
    {
        'app': 'main',
        'label': COMPANY_NICKNAME,
        'models': (
            'main.Vendor',
            'main.Item'
        )
    },
    {
        'app': 'premier',
        'label': 'premier',
        'models': (
            {
                'model': 'premier.PremierManufacturer',
                'label': 'Manufacturers'
            },
            {
                'model': 'premier.PremierProduct',
                'label': 'Products'
            },
        )
    },
    {
        'app': 'sema',
        'label': 'sema',
        'models': (
            {
                'model': 'sema.SemaBrand',
                'label': 'Brands'
            },
            {
                'model': 'sema.SemaDataset',
                'label': 'Datasets'
            },
            {
                'model': 'sema.SemaYear',
                'label': 'Years'
            },
            {
                'model': 'sema.SemaMake',
                'label': 'Makes'
            },
            {
                'model': 'sema.SemaModel',
                'label': 'Models'
            },
            {
                'model': 'sema.SemaSubmodel',
                'label': 'Submodels'
            },
            {
                'model': 'sema.SemaMakeYear',
                'label': 'Make Years'
            },
            {
                'model': 'sema.SemaBaseVehicle',
                'label': 'Base Vehicles'
            },
            {
                'model': 'sema.SemaVehicle',
                'label': 'Vehicles'
            },
            {
                'model': 'sema.SemaCategory',
                'label': 'Categories'
            },
            {
                'model': 'sema.SemaProduct',
                'label': 'Products'
            },
            {
                'model': 'sema.SemaDescriptionPiesAttribute',
                'label': 'Description PIES'  # TODO remove
            },
            {
                'model': 'sema.SemaDigitalAssetsPiesAttribute',
                'label': 'Digital Assets PIES'  # TODO remove
            }
        )
    }
)
