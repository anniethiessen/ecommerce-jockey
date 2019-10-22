import os


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
    'product.apps.ProductAppConfig',  # TODO
    'core.apps.CoreAppConfig',
    'main.apps.MainAppConfig',
    'premier.apps.PremierAppConfig',
    'sema.apps.SemaAppConfig',
    'shopify.apps.ShopifyAppConfig',
    'admin_reorder',
    'import_export'
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
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ]
        }
    }
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
    }
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


ROOT_URLCONF = 'dieselrecommerce.urls'
WSGI_APPLICATION = 'dieselrecommerce.wsgi.application'

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
        'app': 'product',
        'label': 'dieselr',
        'models': (
            'product.Vendor',
            'product.Product'
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
        'app': 'product',
        'label': 'sema',
        'models': (
            {
                'model': 'product.SemaBrand',
                'label': 'Brands'
            },
            {
                'model': 'product.SemaDataset',
                'label': 'Datasets'
            },
            {
                'model': 'product.SemaYear',
                'label': 'Years'
            },
            {
                'model': 'product.SemaMake',
                'label': 'Makes'
            },
            {
                'model': 'product.SemaModel',
                'label': 'Models'
            },
            {
                'model': 'product.SemaSubmodel',
                'label': 'Submodels'
            },
            {
                'model': 'product.SemaMakeYear',
                'label': 'Make Years'
            },
            {
                'model': 'product.SemaBaseVehicle',
                'label': 'Base Vehicles'
            },
            {
                'model': 'product.SemaVehicle',
                'label': 'Vehicles'
            },
            {
                'model': 'product.SemaCategory',
                'label': 'Categories'
            },
            {
                'model': 'product.SemaProduct',
                'label': 'Products'
            }
        )
    }
)


# --- CONSTANTS ---
COMPANY_NAME = 'DIESELR Corp.'
COMPANY_SITE = 'https://www.dieselrcorp.com'

GOOGLE_DRIVE_API_KEY = os.environ['GOOGLE_DRIVE_API_KEY']

PREMIER_BASE_URL = 'https://api.premierwd.com/api/v5'
PREMIER_API_KEY = os.environ['PREMIER_API_KEY']

SEMA_BASE_URL = 'https://sdc.semadatacoop.org/sdcapi'
SEMA_USERNAME = 'AThiessen'
SEMA_PASSWORD = os.environ['SEMA_PASSWORD']
