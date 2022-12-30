import os

from minio.error import S3Error

from minio import Minio

client = Minio(
    os.getenv('MINIO_HOST'),
    access_key=os.getenv('MINIO_ACCESS_KEY'),
    secret_key=os.getenv('MINIO_SECRET_KEY'),
    secure=os.getenv('MINIO_SECURE', 0) == 1
)


class MinioError(Exception):
    pass


def generate_custom_source_url(file_name):
    protocol = 'http'
    if os.getenv('MINIO_SECURE', 0) == 1:
        protocol = 'https'

    return f"{protocol}://{os.getenv('MINIO_HOST')}/{file_name}"


def put_object(source_name, file_upload):
    try:
        client.put_object(
            bucket_name='source--custom',
            object_name=f"/{source_name}/{file_upload.name}",
            data=file_upload,
            length=file_upload.size
        )
    except S3Error as error:
        print(error)
        raise MinioError


def delete_custom_source_bucket(custom_source):
    root_bucket_name = 'source--custom'
    delete_object_list = map(
        lambda x: x.object_name,
        client.list_objects(root_bucket_name, custom_source, recursive=True),
    )

    for delete_object in delete_object_list:
        client.remove_object(root_bucket_name, delete_object)
