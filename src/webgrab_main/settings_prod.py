from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['localhost']

INSTALLED_APPS += ['storages']

AWS_ACCESS_KEY_ID = os.environ.get('S3_ACCESS_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_KEY')
AWS_STORAGE_BUCKET_NAME = 'webgrab'
AWS_S3_CUSTOM_DOMAIN = 's3.eu-north-1.amazonaws.com/%s' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
