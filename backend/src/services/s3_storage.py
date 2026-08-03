"""Async-safe access to private S3 objects using the standard AWS credential chain."""

import os
import uuid
from functools import partial
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from starlette.concurrency import run_in_threadpool


class S3StorageError(Exception):
    pass


class S3Storage:
    def __init__(self, client=None):
        self.bucket = os.getenv("S3_BUCKET_NAME", "")
        self.region = os.getenv("AWS_REGION", "eu-west-1")
        self.client = client or boto3.client("s3", region_name=self.region)

    def _configured(self):
        if not self.bucket:
            raise S3StorageError("CV storage is not configured")

    async def exists(self, key):
        self._configured()
        try:
            await run_in_threadpool(
                self.client.head_object, Bucket=self.bucket, Key=key
            )
            return True
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in (
                "404",
                "NoSuchKey",
                "NotFound",
            ):
                return False
            raise S3StorageError("CV storage is temporarily unavailable") from None
        except BotoCoreError:
            raise S3StorageError("CV storage is temporarily unavailable") from None

    async def presigned_download(self, key, filename, expiry):
        self._configured()
        params = {
            "Bucket": self.bucket,
            "Key": key,
            "ResponseContentType": "application/pdf",
            "ResponseContentDisposition": f'attachment; filename="{filename}"',
        }
        try:
            return await run_in_threadpool(
                partial(
                    self.client.generate_presigned_url,
                    "get_object",
                    Params=params,
                    ExpiresIn=expiry,
                )
            )
        except (BotoCoreError, ClientError):
            raise S3StorageError("CV download could not be prepared") from None

    async def upload_pdf(self, data):
        self._configured()
        prefix = os.getenv("S3_UPLOAD_PREFIX", "cv/uploads").strip("/")
        key = f"{prefix}/{uuid.uuid4()}.pdf"
        try:
            await run_in_threadpool(
                self.client.put_object,
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType="application/pdf",
            )
        except (BotoCoreError, ClientError):
            raise S3StorageError("CV upload is temporarily unavailable") from None
        return key

    async def download(self, key):
        self._configured()
        try:
            response = await run_in_threadpool(
                self.client.get_object, Bucket=self.bucket, Key=key
            )
            return await run_in_threadpool(response["Body"].read)
        except (BotoCoreError, ClientError):
            raise S3StorageError("CV file is temporarily unavailable") from None

    async def delete(self, key):
        self._configured()
        public = os.getenv("S3_PUBLIC_CV_KEY", "cv/public/tshimbiluni-nedambale-cv.pdf")
        if key == public:
            raise S3StorageError("The public CV cannot be deleted")
        try:
            await run_in_threadpool(
                self.client.delete_object, Bucket=self.bucket, Key=key
            )
        except (BotoCoreError, ClientError):
            raise S3StorageError("Temporary CV cleanup failed") from None
