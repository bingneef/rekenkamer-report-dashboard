from minio import Minio
from minio.error import S3Error
import io
import os
from dotenv import load_dotenv


load_dotenv()

minio_host = os.environ['MINIO_HOST']
client = Minio(
    minio_host,
    access_key=os.environ['MINIO_ACCESS_KEY'],
    secret_key=os.environ['MINIO_SECRET_KEY'],
    secure=os.environ.get('MINIO_SECURE', 0) == 1
)
