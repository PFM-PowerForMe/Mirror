import boto3


class S3:
    def __init__(self, endpoint_url, aws_access_key_id, aws_secret_access_key, bucket_name):
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket_name = bucket_name
        self.s3 = boto3.resource('s3',
                                 endpoint_url=self.endpoint_url,
                                 aws_access_key_id=self.aws_access_key_id,
                                 aws_secret_access_key=self.aws_secret_access_key)
        self.bucket = self.s3.Bucket(self.bucket_name)

    def verify_file(self, obj_path) -> bool:
        return any(self.bucket.objects.filter(Prefix=obj_path))

    def download_file(self, obj_path, local_path):
        self.bucket.download_file(obj_path, local_path)

    def upload_file(self, local_path, obj_path):
        self.bucket.upload_file(local_path, obj_path)

    def delete_file(self, obj_path):
        self.s3.Object(self.bucket_name, obj_path).delete()
