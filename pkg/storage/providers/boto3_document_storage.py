from pkg.storage.settings import settings
import boto3  # type: ignore
from pkg.storage.retriever_document_storage import RetrieverDocumentStorage


class Boto3DocumentStorage(RetrieverDocumentStorage):
    def __init__(self) -> None:
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.bucket_endpoint,
            aws_access_key_id=settings.key_id,
            aws_secret_access_key=settings.key_secret,
            region_name=settings.bucket_region,
        )

    def get_bytes(self, file_uuid: str) -> bytes:
        content = self.s3.get_object(Bucket=settings.bucket, Key=file_uuid)[
            "Body"
        ].read()
        return content

    def download(self, file_uuid: str, path: str) -> None:
        self.s3.download_file(Bucket=settings.bucket, Key=file_uuid, Filename=path)
