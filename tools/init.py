import os


class Init:
    def __init__(self):
        self.gpg_keyid = os.environ.get('GPG_KEYID')
        self.cloudflare_account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
        self.endpoint_url = f'https://{self.cloudflare_account_id}.r2.cloudflarestorage.com'
        self.aws_access_key_id = os.environ.get('CLOUDFLARE_R2_TOKEN_KEY_ID')
        self.aws_secret_access_key = os.environ.get('CLOUDFLARE_R2_TOKEN_SECRET')
        self.bucket_name = os.environ.get('R2_BUCKET_NAME')
        self.work_dir = os.environ.get('WORK_DIR')
        self.work_x64_dir = f'{self.work_dir}/work/x86_64'
        self.work_aarch64_dir = f'{self.work_dir}/work/aarch64'
        self.build_dir = f'{self.work_dir}/work/build_tmp'
        self.build_x64_dir = f'{self.build_dir}/x86_64'
        self.build_aarch64_dir = f'{self.build_dir}/aarch64'

        for directory in [self.work_dir, self.work_x64_dir, self.work_aarch64_dir, self.build_dir, self.build_x64_dir, self.build_aarch64_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def get_gpg_keyid(self) -> str:
        if self.gpg_keyid is None:
            raise Exception("GPG_KEYID not set")
        return self.gpg_keyid

    def get_cloudflare_account_id(self) -> str:
        if self.cloudflare_account_id is None:
            raise Exception("CLOUDFLARE_ACCOUNT_ID not set")
        return self.cloudflare_account_id

    def get_endpoint_url(self) -> str:
        return self.endpoint_url

    def get_aws_access_key_id(self) -> str:
        if self.aws_access_key_id is None:
            raise Exception("CLOUDFLARE_R2_TOKEN_KEY_ID not set")
        return self.aws_access_key_id

    def get_aws_secret_access_key(self) -> str:
        if self.aws_secret_access_key is None:
            raise Exception("CLOUDFLARE_R2_TOKEN_SECRET not set")
        return self.aws_secret_access_key

    def get_bucket_name(self) -> str:
        if self.bucket_name is None:
            raise Exception("R2_BUCKET_NAME not set")
        return self.bucket_name

    def get_work_dir(self) -> str:
        if self.work_dir is None:
            raise Exception("WORK_DIR not set")
        return self.work_dir
    
    def get_work_x64_dir(self) -> str:
        return self.work_x64_dir
    
    def get_work_aarch64_dir(self) -> str:
        return self.work_aarch64_dir
    
    def get_build_dir(self) -> str:
        return self.build_dir
    
    def get_build_x64_dir(self) -> str:
        return self.build_x64_dir
    
    def get_build_aarch64_dir(self) -> str:
        return self.build_aarch64_dir