from unittest import TestCase

from django.core.files.storage import Storage
from storages.backends.s3boto3 import S3Boto3Storage

from report_submission.storages import S3PublicStorage, S3PrivateStorage


class TestStorages(TestCase):
    def test_public_storage_type(self):
        public_storage = S3PublicStorage()
        self.assertIsInstance(public_storage, S3PublicStorage)
        self.assertIsInstance(public_storage, S3Boto3Storage)
        self.assertIsInstance(public_storage, Storage)

    def test_private_storage_type(self):
        private_storage = S3PrivateStorage()
        self.assertIsInstance(private_storage, S3PrivateStorage)
        self.assertIsInstance(private_storage, S3Boto3Storage)
        self.assertIsInstance(private_storage, Storage)
