from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage, S3ManifestStaticStorage


class S3PrivateStorage(S3Boto3Storage):
    bucket_name = settings.AWS_PRIVATE_STORAGE_BUCKET_NAME
    access_key = settings.AWS_PRIVATE_ACCESS_KEY_ID
    secret_key = settings.AWS_PRIVATE_SECRET_ACCESS_KEY


class S3PublicStorage(S3ManifestStaticStorage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    access_key = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
