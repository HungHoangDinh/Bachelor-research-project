from minio import Minio
import os

minio_client = Minio(
    "minio:9000",
    access_key=os.environ["MINIO_ROOT_USER"],
    secret_key=os.environ["MINIO_ROOT_PASSWORD"],
    secure=False,
)
bucket_name = "files"
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)