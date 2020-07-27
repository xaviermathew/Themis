from storages.backends.s3boto3 import S3Boto3Storage


class S3GlacierStorage(S3Boto3Storage):
    object_parameters = {'StorageClass': 'GLACIER'}


def upload_to_s3(ip_path, dest_path, storage_class=S3Boto3Storage):
    storage = storage_class()
    file_obj = open(ip_path, mode='rb')
    return storage.save(dest_path, file_obj)


def upload_to_glacier(ip_path, dest_path):
    return upload_to_s3(ip_path, dest_path, storage_class=S3GlacierStorage)
