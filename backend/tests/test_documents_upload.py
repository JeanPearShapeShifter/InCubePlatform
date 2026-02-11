import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.errors import ValidationError
from app.services.minio import ALLOWED_TYPES, MAX_FILE_SIZE, _sanitize_filename, upload_file


class TestFileValidation:
    @pytest.mark.asyncio
    async def test_upload_rejects_empty_file(self):
        client = MagicMock()
        with pytest.raises(ValidationError, match="empty"):
            await upload_file(client, b"", "test.pdf", "application/pdf", str(uuid.uuid4()))

    @pytest.mark.asyncio
    async def test_upload_rejects_oversized_file(self):
        client = MagicMock()
        data = b"x" * (MAX_FILE_SIZE + 1)
        with pytest.raises(ValidationError, match="maximum size"):
            await upload_file(client, data, "big.pdf", "application/pdf", str(uuid.uuid4()))

    @pytest.mark.asyncio
    async def test_upload_rejects_disallowed_type(self):
        client = MagicMock()
        with pytest.raises(ValidationError, match="not allowed"):
            await upload_file(client, b"data", "test.exe", "application/x-msdownload", str(uuid.uuid4()))

    @pytest.mark.asyncio
    async def test_upload_accepts_allowed_types(self):
        for content_type in ALLOWED_TYPES:
            client = AsyncMock()
            client.bucket_exists = AsyncMock(return_value=True)
            client.put_object = AsyncMock()

            key = await upload_file(client, b"data", "test.file", content_type, str(uuid.uuid4()))
            assert key.startswith("perspectives/")
            assert client.put_object.called

    @pytest.mark.asyncio
    async def test_upload_creates_bucket_if_missing(self):
        client = AsyncMock()
        client.bucket_exists = AsyncMock(return_value=False)
        client.make_bucket = AsyncMock()
        client.put_object = AsyncMock()

        await upload_file(client, b"data", "test.pdf", "application/pdf", str(uuid.uuid4()))
        client.make_bucket.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_key_format(self):
        perspective_id = str(uuid.uuid4())
        client = AsyncMock()
        client.bucket_exists = AsyncMock(return_value=True)
        client.put_object = AsyncMock()

        key = await upload_file(client, b"data", "my report.pdf", "application/pdf", perspective_id)
        assert key.startswith(f"perspectives/{perspective_id}/")
        assert "my_report.pdf" in key


class TestSanitizeFilename:
    def test_removes_spaces(self):
        assert _sanitize_filename("my file.pdf") == "my_file.pdf"

    def test_removes_path_traversal(self):
        result = _sanitize_filename("../../etc/passwd")
        assert "/" not in result
        assert ".." not in result or result == "..etc..passwd"  # Just the filename part

    def test_keeps_safe_characters(self):
        assert _sanitize_filename("report-2024_v2.pdf") == "report-2024_v2.pdf"

    def test_removes_special_characters(self):
        result = _sanitize_filename("file<>name.pdf")
        assert "<" not in result
        assert ">" not in result


class TestDocumentServiceMocked:
    @pytest.mark.asyncio
    async def test_create_document_calls_minio(self):
        with (
            patch("app.services.document.get_minio_client") as mock_client_fn,
            patch("app.services.document.upload_file") as mock_upload,
        ):
            mock_client = MagicMock()
            mock_client_fn.return_value = mock_client
            mock_upload.return_value = "perspectives/test/uuid_file.pdf"

            mock_file = AsyncMock()
            mock_file.read = AsyncMock(return_value=b"pdf content")
            mock_file.content_type = "application/pdf"
            mock_file.filename = "test.pdf"

            mock_db = AsyncMock()
            mock_db.add = MagicMock()
            mock_db.flush = AsyncMock()

            from app.services.document import create_document

            doc = await create_document(mock_db, uuid.uuid4(), uuid.uuid4(), mock_file)
            mock_upload.assert_called_once()
            mock_db.add.assert_called_once()
            assert doc.filename == "test.pdf"
            assert doc.file_type == "application/pdf"

    @pytest.mark.asyncio
    async def test_delete_document_removes_from_minio(self):
        with (
            patch("app.services.document.get_minio_client") as mock_client_fn,
            patch("app.services.document.delete_file") as mock_delete,
        ):
            mock_client = MagicMock()
            mock_client_fn.return_value = mock_client

            mock_doc = MagicMock()
            mock_doc.minio_key = "perspectives/test/uuid_file.pdf"

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_doc

            mock_db = AsyncMock()
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_db.delete = AsyncMock()
            mock_db.flush = AsyncMock()

            from app.services.document import delete_document

            await delete_document(mock_db, uuid.uuid4())
            mock_delete.assert_called_once_with(mock_client, "perspectives/test/uuid_file.pdf")
            mock_db.delete.assert_called_once_with(mock_doc)
