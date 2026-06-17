import boto3
import uuid
from botocore.exceptions import ClientError
from botocore.config import Config
from fastapi import UploadFile
from app.core.config import settings
import logging

log = logging.getLogger(__name__)

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
    config=Config(signature_version="s3v4"),
)

ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
    "text/csv": ".csv",
}
MAX_SIZE_MB = 50


async def upload_file(file: UploadFile, user_id: int) -> dict:
    if file.content_type not in ALLOWED_TYPES:
        raise ValueError(f"Unsupported file type: {file.content_type}")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise ValueError(f"File too large: {size_mb:.1f}MB (max {MAX_SIZE_MB}MB)")

    ext = ALLOWED_TYPES[file.content_type]
    key = f"users/{user_id}/documents/{uuid.uuid4()}{ext}"

    try:
        s3.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=content,
            ContentType=file.content_type,
            Metadata={"original_name": file.filename, "user_id": str(user_id)},
        )
        log.info("Uploaded %s -> %s", file.filename, key)
        return {
            "s3_key": key,
            "original_name": file.filename,
            "size_bytes": len(content),
            "content_type": file.content_type,
        }
    except ClientError as e:
        log.error("S3 upload failed: %s", e)
        raise RuntimeError("Upload failed") from e


def get_presigned_url(s3_key: str, expires: int = 3600) -> str:
    try:
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": s3_key},
            ExpiresIn=expires,
        )
    except ClientError as e:
        log.error("Presigned URL failed: %s", e)
        raise RuntimeError("Could not generate URL") from e


def delete_file(s3_key: str) -> bool:
    try:
        s3.delete_object(Bucket=settings.S3_BUCKET, Key=s3_key)
        log.info("Deleted S3 key: %s", s3_key)
        return True
    except ClientError as e:
        log.error("S3 delete failed: %s", e)
        return False


def list_user_files(user_id: int) -> list[dict]:
    prefix = f"users/{user_id}/documents/"
    try:
        resp = s3.list_objects_v2(Bucket=settings.S3_BUCKET, Prefix=prefix)
        files = []
        for obj in resp.get("Contents", []):
            head = s3.head_object(Bucket=settings.S3_BUCKET, Key=obj["Key"])
            files.append({
                "s3_key": obj["Key"],
                "size_bytes": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
                "original_name": head.get("Metadata", {}).get("original_name", ""),
            })
        return files
    except ClientError as e:
        log.error("S3 list failed: %s", e)
        return []
