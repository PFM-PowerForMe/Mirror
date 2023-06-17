import json
import shutil
import subprocess
from tools.s3 import S3
import logging

class Build():
    def __init__(self, r2: S3, x64_build_data: str, aarch64_build_data: str, build_x64_dir: str, build_aarch64_dir: str, work_x64_dir: str, work_aarch64_dir: str, gpg_keyid: str, logger: logging.Logger):
        """
        Build packages
        x64_build_data: json string of x64 build data
        aarch64_build_data: json string of aarch64 build data
        build_x64_dir: directory to build x64 packages
        build_aarch64_dir: directory to build aarch64 packages
        work_x64_dir: directory to store x64 packages
        work_aarch64_dir: directory to store aarch64 packages
        r2: S3 object
        gpg_keyid: GPG keyid
        """
        self.x64_build_data = json.loads(x64_build_data)
        self.aarch64_build_data = json.loads(aarch64_build_data)
        self.build_x64_dir = build_x64_dir
        self.build_aarch64_dir = build_aarch64_dir
        self.work_x64_dir = work_x64_dir
        self.work_aarch64_dir = work_aarch64_dir
        self.r2 = r2
        self.gpg_keyid = gpg_keyid
        self.logger = logger

    def run(self) -> bool:
        flag_x64 = False
        flag_aarch64 = False
        for tablename, table in self.x64_build_data["pkg"].items():
            try:
                self._build_x86_64(tablename, table)
            except Exception as exc:
                self.logger.error(f'x86_64 Package {tablename} failed with exception: {exc}')
                flag_x64 = False
                break
            self.logger.info(f'x86_64 Package {tablename} done')
            flag_x64 = True
        for tablename, table in self.aarch64_build_data["pkg"].items():
            try:
                self._build_aarch64(tablename, table)
            except Exception as exc:
                self.logger.error(f'aarch64 Package {tablename} failed with exception: {exc}')
                flag_aarch64 = False
                break
            self.logger.info(f'aarch64 Package {tablename} done')
            flag_aarch64 = True
        if flag_x64 and flag_aarch64:
            return True
        else:
            return False

    def _build_x86_64(self, tablename, table):
        try:
            subprocess.run(f'cd {self.build_x64_dir}/{tablename} && makepkg -sA --noconfirm --sign --key {self.gpg_keyid}', check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.logger.info(f'x86_64 Build {tablename} done')
        except subprocess.CalledProcessError as e:
            self.logger.error(f'x86_64 Build {tablename} failed with exception: {e}')
            self.logger.error(f'x86_64 Build {tablename} failed with stdeer: {e.stderr.decode()}')
            exit(1)
        shutil.move(f"{self.build_x64_dir}/{tablename}/{tablename}-{table['Version']}-x86_64.pkg.tar.zst",
                    f"{self.work_x64_dir}/{tablename}-{table['Version']}-x86_64.pkg.tar.zst")
        shutil.move(f"{self.build_x64_dir}/{tablename}/{tablename}-{table['Version']}-x86_64.pkg.tar.zst.sig",
                    f"{self.work_x64_dir}/{tablename}-{table['Version']}-x86_64.pkg.tar.zst.sig")
        if not table["isnew"]:
            self.r2.delete_file(f'ArchLinuxPFM/x86_64/{table["s3filename"]}')
        try:
            subprocess.run(f'repo-add -s {self.work_x64_dir}/ArchLinuxPFM.db.tar.gz {self.work_x64_dir}/{tablename}-{table["Version"]}-x86_64.pkg.tar.zst', check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            self.logger.error(f'x86_64 repo-add {tablename} failed with exception: {e}')
            self.logger.error(f'x86_64 repo-add {tablename} failed with stdeer: {e.stderr.decode()}')
            exit(1)

    def _build_aarch64(self, tablename, table):
        try:
            subprocess.run(f'cd {self.build_aarch64_dir}/{tablename} && CARCH=aarch64 ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- makepkg -sA --noconfirm --sign --key {self.gpg_keyid}', check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.logger.info(f'aarch64 Build {tablename} done')
        except subprocess.CalledProcessError as e:
            self.logger.error(f'aarch64 Build {tablename} failed with exception: {e}')
            self.logger.error(f'aarch64 Build {tablename} failed with stdeer: {e.stderr.decode()}')
            exit(1)
        shutil.move(f"{self.build_aarch64_dir}/{tablename}/{tablename}-{table['Version']}-aarch64.pkg.tar.zst",
                    f"{self.work_aarch64_dir}/{tablename}-{table['Version']}-aarch64.pkg.tar.zst")
        shutil.move(f"{self.build_aarch64_dir}/{tablename}/{tablename}-{table['Version']}-aarch64.pkg.tar.zst.sig",
                    f"{self.work_aarch64_dir}/{tablename}-{table['Version']}-aarch64.pkg.tar.zst.sig")
        if not table["isnew"]:
            self.r2.delete_file(f'ArchLinuxPFM/aarch64/{table["s3filename"]}')
        try:
            subprocess.run(f'repo-add -s {self.work_aarch64_dir}/ArchLinuxPFM.db.tar.gz {self.work_aarch64_dir}/{tablename}-{table["Version"]}-aarch64.pkg.tar.zst', check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            self.logger.error(f'aarch64 repo-add {tablename} failed with exception: {e}')
            self.logger.error(f'aarch64 repo-add {tablename} failed with stdeer: {e.stderr.decode()}')
            exit(1)

