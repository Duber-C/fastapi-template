import os
import mimetypes
import uuid
import boto3
import shutil
import magic
from urllib.parse import urlparse
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import UploadFile, HTTPException
from fastapi.concurrency import run_in_threadpool

from src.settings import EnvironmentEnum, settings


class FileInterface(ABC):
    allowed_mimes: Optional[list[str]] = None
    base_url: str

    def __init__(
        self,
        file: UploadFile
    ):
        self.file = file

    def validate(self):
        if not self.allowed_mimes:
            return
        if self.file.content_type not in self.allowed_mimes:
            pos = self.file.file.tell()
            try:
                head = self.file.file.read(2048)
            finally:
                self.file.file.seek(pos)
            sniffed = magic.from_buffer(head, mime=True) if head else None
            if sniffed not in self.allowed_mimes:
                raise HTTPException(400, "Invalid image type")

    @abstractmethod
    async def save(self) -> str:
        ...

    @abstractmethod
    async def delete(self, image_url: str):
        ...


class StaticFile(FileInterface):
    base_dir: str = "files"
    base_url: str = "/files"

    async def save(self) -> str:
        self.validate()

        os.makedirs(self.base_dir, exist_ok=True)

        if not self.file.filename:
            raise HTTPException(400, "File does not have a filename")
        ext = os.path.splitext(self.file.filename)[1]

        filename = f"{uuid.uuid4()}{ext}"
        path = os.path.join(self.base_dir, filename)

        def _write_file() -> None:
            self.file.file.seek(0)
            with open(path, "wb") as f:
                shutil.copyfileobj(self.file.file, f)

        await run_in_threadpool(_write_file)

        return f"{self.base_url}/{filename}"

    async def delete(self, image_url: str):
        if not image_url:
            raise HTTPException(400, "image_url not defined")


        parsed = urlparse(image_url) if "://" in image_url else None
        if parsed:
            relative = parsed.path
        elif self.base_url and image_url.startswith(self.base_url):
            relative = image_url[len(self.base_url):]
        else:
            relative = image_url

        relative = relative.lstrip("/")
        base_dir = os.path.abspath(self.base_dir)
        path = os.path.abspath(os.path.join(base_dir, relative))

        if os.path.commonpath([base_dir, path]) != base_dir:
            raise HTTPException(400, "Invalid image path")

        if os.path.exists(path):
            os.remove(path)


class S3File(FileInterface):
    prefix: str = settings.s3_conf.prefix
    bucket: str = settings.s3_conf.bucket
    base_url: str = f"https://{settings.s3_conf.bucket}.s3.{settings.s3_conf.region}.amazonaws.com"
    s3 = boto3.client("s3", region_name=settings.s3_conf.region)

    async def save(self) -> str:
        self.validate()

        if not self.file.content_type:
            raise HTTPException(400, "File does not have a content_type")
        ext = mimetypes.guess_extension(self.file.content_type) or ""
        key = f"{self.prefix}/{uuid.uuid4()}{ext}"

        await run_in_threadpool(
            self.s3.upload_fileobj,
            self.file.file,
            self.bucket,
            key,
            ExtraArgs={
                "ContentType": self.file.content_type,
                "ACL": "public-read",
            },
        )

        return f"{self.base_url}/{key}"

    async def delete(self, image_url: str):
        parsed = urlparse(image_url) if "://" in image_url else None
        base_parsed = urlparse(self.base_url) if "://" in self.base_url else None

        if parsed:
            path = parsed.path.lstrip("/")
            base_path = base_parsed.path.rstrip("/") if base_parsed else self.base_url.rstrip("/")
            if base_path and path.startswith(base_path.lstrip("/") + "/"):
                key = path[len(base_path.lstrip("/")) + 1:]
            else:
                key = path
        else:
            base_path = self.base_url.lstrip("/")
            path = image_url.lstrip("/")
            if base_path and path.startswith(base_path + "/"):
                key = path[len(base_path) + 1:]
            else:
                key = path

        if not key.startswith(f"{self.prefix}/"):
            raise HTTPException(400, "Invalid image path")

        await run_in_threadpool(
            self.s3.delete_object,
            Bucket=self.bucket,
            Key=key,
        )


def get_file_manager():
    if settings.environment == EnvironmentEnum.prod:
        return S3File

    return StaticFile

file_manager = get_file_manager()
