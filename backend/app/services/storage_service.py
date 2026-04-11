from pathlib import Path

import boto3

from app.core.config import settings


def upload_resume_stub(user_id: str, filename: str) -> str:
    if settings.s3_bucket and settings.aws_access_key_id and settings.aws_secret_access_key:
        boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
        return f"https://{settings.s3_bucket}.s3.{settings.aws_region}.amazonaws.com/resumes/{user_id}/{filename}"
    return f"https://storage.local/resumes/{user_id}/{Path(filename).name}"
