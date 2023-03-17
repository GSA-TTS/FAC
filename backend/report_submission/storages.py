from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class S3PrivateStorage(S3Boto3Storage):
    """
    This class exists to help django-storages work with two S3 buckets. S3Boto
    will work with one bucket, but trying to swap between two is complicated. Adding
    this storage method then specifying it in settings.py (instead of S3Boto itself)
    lets it use the alternative bucket.
    """

    bucket_name = settings.AWS_PRIVATE_STORAGE_BUCKET_NAME
    access_key = settings.AWS_PRIVATE_ACCESS_KEY_ID
    secret_key = settings.AWS_PRIVATE_SECRET_ACCESS_KEY
    location = ""
