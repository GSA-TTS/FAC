from django.test import TestCase
from django.conf import settings
from django.db import connections

import boto3


class SettingsTestCase(TestCase):
    def test_db(self):
        databases = settings.DATABASES
        self.assertEquals(len(databases), 2)

        for db in databases:
            connection = str(connections[db])
            self.assertTrue(db in connection)

    def test_private_s3(self):
        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            )
            self.assertIsNotNone(s3_client)
            items = s3_client.list_objects(
                Bucket=settings.AWS_PRIVATE_STORAGE_BUCKET_NAME,
            )
            self.assertIsNotNone(items)
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    def test_c2g_s3(self):
        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            )
            self.assertIsNotNone(s3_client)
            items = s3_client.list_objects(
                Bucket=settings.AWS_C2F_BUCKET_NAME,
            )
            self.assertIsNotNone(items)
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")
