from django.test import TestCase
from django.conf import settings


import boto3

from census_historical_migration.models import ELECAUDITHEADER as Gen
from audit.models import SingleAuditChecklist


class SettingsTestCase(TestCase):
    databases = {"default"}

    def test_models_are_in_appropriate_db(self):
        sacs = SingleAuditChecklist.objects.all()
        self.assertEqual(len(sacs), 0)
        gens = Gen.objects.using("default").all()
        self.assertEqual(len(gens), 0)

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
                Bucket=settings.AWS_PRIVATE_STORAGE_BUCKET_NAME,
            )
            self.assertIsNotNone(items)
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")
