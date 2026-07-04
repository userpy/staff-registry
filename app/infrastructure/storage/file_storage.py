import logging
from pathlib import Path
from uuid import uuid4

import aiofiles

from app.application.exceptions import FileUploadException
from app.application.ports.file_storage import UploadedFile

logger = logging.getLogger(__name__)


class FileStorage:
    def __init__(
        self,
        upload_directory: Path,
        upload_url_prefix: str,
        allowed_extensions: frozenset[str],
        max_size_bytes: int,
    ) -> None:
        self.upload_directory = upload_directory
        self.upload_url_prefix = upload_url_prefix.rstrip("/")
        self.allowed_extensions = allowed_extensions
        self.max_size_bytes = max_size_bytes

    async def save(self, upload_file: UploadedFile | None) -> str | None:
        if upload_file is None or not upload_file.filename:
            return None

        extension = upload_file.filename.rsplit(".", 1)[-1].lower()
        if extension not in self.allowed_extensions:
            message = "Фото должно быть файлом jpg, jpeg или png."
            logger.warning("file_upload_error", extra={"reason": message})
            raise FileUploadException(message=message, errors={"photo": message})

        content = await upload_file.read()
        if len(content) > self.max_size_bytes:
            message = "Фото должно быть не больше 200 КБ."
            logger.warning("file_upload_error", extra={"reason": message})
            raise FileUploadException(message=message, errors={"photo": message})

        if not content:
            message = "Загруженное фото пустое."
            logger.warning("file_upload_error", extra={"reason": message})
            raise FileUploadException(message=message, errors={"photo": message})

        self.upload_directory.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4().hex}.{extension}"
        destination = self.upload_directory / filename

        try:
            async with aiofiles.open(destination, "wb") as file:
                await file.write(content)
        except OSError as exc:
            logger.exception("file_upload_save_failed")
            raise FileUploadException(
                message="Не удалось сохранить загруженное фото.",
                errors={"photo": "Не удалось сохранить файл."},
            ) from exc

        return f"{self.upload_url_prefix}/{filename}"

    async def delete(self, file_url: str | None) -> None:
        if not file_url:
            return
        filename = file_url.rsplit("/", 1)[-1]
        file_path = self.upload_directory / filename
        try:
            file_path.unlink(missing_ok=True)
        except OSError:
            logger.warning("file_delete_failed", extra={"file_path": str(file_path)})
