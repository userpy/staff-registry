from typing import Protocol


class UploadedFile(Protocol):
    filename: str | None

    async def read(self) -> bytes:
        raise NotImplementedError


class FileStoragePort(Protocol):
    async def save(self, upload_file: UploadedFile | None) -> str | None:
        raise NotImplementedError

    async def delete(self, file_url: str | None) -> None:
        raise NotImplementedError
