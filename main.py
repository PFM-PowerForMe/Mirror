import json
import re
import shutil
import sys
import urllib.request
import tarfile
import os
import logging
from tools.init import Init
from tools.s3 import S3
from tools.package import Package
from tools.pjdb import Pjdb
from tools.packagecomparator import PackageComparator
from tools.build import Build
from tools.check_depends import CheckDepends


def gen_config(str_x64_build_data: str, str_aarch64_build_data: str, work_dir: str, build_dir: str, build_x64_dir: str,build_aarch64_dir: str):
    """
    Generate config
    :param str_x64_build_data: x64 build data
    :param str_aarch64_build_data: aarch64 build data
    :param work_dir: work dir
    :param build_dir: build dir
    :param build_x64_dir: x64 build dir
    :param build_aarch64_dir: aarch64 build dir
    :return: None
    """
    x64_build_data = json.loads(str_x64_build_data)
    aarch64_build_data = json.loads(str_aarch64_build_data)
    for tablename, table in x64_build_data["pkg"].items():
        if "api_interface" in table:
            if table["api_interface"] != "AUR":
                shutil.copytree(f"{work_dir}/build_config/{tablename}",
                                f"{build_x64_dir}/{tablename}",
                                symlinks=False,
                                ignore=None,
                                ignore_dangling_symlinks=False,
                                dirs_exist_ok=True)
                with open(f"{build_x64_dir}/{tablename}/PKGBUILD" , 'r+', encoding='UTF-8') as f:
                    content = f.read()
                    f.seek(0, 0)
                    f.write(f"_pkgname={tablename}\n")
                    f.write(f"_version={table['PKGBUILD']['version']}\n")
                    f.write(f"_pkgrel={table['PKGBUILD']['pkgrel']}\n")
                    f.write(content)
            else:
                url = table["URLPath"]
                urllib.request.urlretrieve(
                    url, f"{build_dir}/{tablename}.tar.gz")
                with tarfile.open(f"{build_dir}/{tablename}.tar.gz") as tar:
                    tar.extractall(f"{build_x64_dir}/")
                    os.remove(f"{build_dir}/{tablename}.tar.gz")

    for tablename, table in aarch64_build_data["pkg"].items():
        if "api_interface" in table:
            if table["api_interface"] != "AUR":
                shutil.copytree(f"{work_dir}/build_config/{tablename}",
                                f"{build_aarch64_dir}/{tablename}",
                                symlinks=False,
                                ignore=None,
                                ignore_dangling_symlinks=False,
                                dirs_exist_ok=True)
                with open(f"{build_aarch64_dir}/{tablename}/PKGBUILD", 'r+', encoding='UTF-8') as f:
                    content = f.read()
                    f.seek(0, 0)
                    f.write(f"_pkgname={tablename}\n")
                    f.write(f"_version={table['PKGBUILD']['version']}\n")
                    f.write(f"_pkgrel={table['PKGBUILD']['pkgrel']}\n")
                    f.write(content)
            else:
                url = table["URLPath"]
                urllib.request.urlretrieve(
                    url, f"{build_dir}/{tablename}.tar.gz")
                with tarfile.open(f"{build_dir}/{tablename}.tar.gz") as tar:
                    tar.extractall(f"{build_aarch64_dir}/")
                    os.remove(f"{build_dir}/{tablename}.tar.gz")

def init_work_dir(r2: S3, work_x64_dir: str, work_aarch64_dir: str) -> bool:
    """
    Init work dir
    :param r2: S3
    :param work_x64_dir: work_x64_dir
    :param work_aarch64_dir: work_aarch64_dir
    :return: bool
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    files = ["ArchLinuxPFM.db", "ArchLinuxPFM.db.sig", "ArchLinuxPFM.db.tar.gz", "ArchLinuxPFM.db.tar.gz.sig", "ArchLinuxPFM.files", "ArchLinuxPFM.files.sig", "ArchLinuxPFM.files.tar.gz", "ArchLinuxPFM.files.tar.gz.sig"]
    if all([r2.verify_file(f"ArchLinuxPFM/x86_64/{file}") for file in files]) and all([r2.verify_file(f"ArchLinuxPFM/aarch64/{file}") for file in files]):
        for file in files:
            logger.info(f"File found x86_64: {file} and aarch64: {file}")
            r2.download_file(f"ArchLinuxPFM/x86_64/{file}", f"{work_x64_dir}/{file}")
            r2.download_file(f"ArchLinuxPFM/aarch64/{file}", f"{work_aarch64_dir}/{file}")
        return True
    else:
        for file in files:
            if not r2.verify_file(f"ArchLinuxPFM/x86_64/{file}"):
                logger.info(f"File not found x86_64: {file}")
            elif not r2.verify_file(f"ArchLinuxPFM/aarch64/{file}"):
                logger.info(f"File not found aarch64: {file}")
            else:
                logger.info(f"File found x86_64: {file} and aarch64: {file}")
        return False



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    config = Init()
    r2 = S3(config.get_endpoint_url(), 
            config.get_aws_access_key_id(),
            config.get_aws_secret_access_key(), 
            config.get_bucket_name())
    
    package_data = Package("Package.toml")
    package_data = package_data.get_versions()

    if init_work_dir(r2, config.get_work_x64_dir(), config.get_work_aarch64_dir()):
        x64_db_data = Pjdb(f"{config.get_work_x64_dir()}/ArchLinuxPFM.db")
        x64_db_data = x64_db_data.to_json()
        aarch64_db_data = Pjdb(f"{config.get_work_aarch64_dir()}/ArchLinuxPFM.db")
        aarch64_db_data = aarch64_db_data.to_json()
        checkdepends = CheckDepends(logger, package_data, x64_db_data)
        check_db_data = checkdepends.check_depends_in_mirror()
        x64_build_data = PackageComparator(x64_db_data, check_db_data)
        x64_build_data = x64_build_data.compare()
        aarch64_build_data = PackageComparator(aarch64_db_data, check_db_data)
        aarch64_build_data = aarch64_build_data.compare()
    else:
        logger.info("No data found in work dir, building all packages")
        x64_new_data = {}
        aarch64_new_data = {}
        package_data = json.loads(package_data)
        for tablename, table in package_data["pkg"].items():
            if "depends_in_mirror" in table:
                if table["depends_in_mirror"] == True:
                    continue
            x64_new_data[tablename] = table
            x64_new_data[tablename]['isnew'] = True
            aarch64_new_data[tablename] = table
            aarch64_new_data[tablename]['isnew'] = True
        x64_build_data = json.dumps({'pkg': x64_new_data}, indent=2)
        aarch64_build_data = json.dumps({'pkg': aarch64_new_data}, indent=2)

    if x64_build_data and aarch64_build_data != None:
        gen_config(x64_build_data, aarch64_build_data, config.get_work_dir(), config.get_build_dir(),config.get_build_x64_dir(), config.get_build_aarch64_dir())
        build = Build(r2, x64_build_data, aarch64_build_data, config.get_build_x64_dir(), config.get_build_aarch64_dir(), config.get_work_x64_dir(), config.get_work_aarch64_dir(), config.get_gpg_keyid(), logger)
        if build.run():
            for root, dirs, files in os.walk(config.work_x64_dir):
                for file in files:
                    r2.upload_file(os.path.join(root, file),
                               f"ArchLinuxPFM/x86_64/{file}")
                    if r2.verify_file(f"ArchLinuxPFM/x86_64/{file}"):
                        logger.info(f"File uploaded x86_64: {file}")
                    else:
                        logger.info(f"File not uploaded x86_64: {file}")
            for root, dirs, files in os.walk(config.work_aarch64_dir):
                for file in files:
                    r2.upload_file(os.path.join(root, file),
                               f"ArchLinuxPFM/aarch64/{file}")
                    if r2.verify_file(f"ArchLinuxPFM/aarch64/{file}"):
                        logger.info(f"File uploaded aarch64: {file}")
                    else:
                        logger.info(f"File not uploaded aarch64: {file}")
        else:
            logger.info("Build failed")
            sys.exit(1)

        
    else:
        logger.info("No new packages found")
        sys.exit(0) 
