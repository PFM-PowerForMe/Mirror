import concurrent.futures
import tomllib
from json import dumps
from tools.github import Github
from tools.aur import Aur

class Package:
    def __init__(self, toml_path):
        with open(toml_path, "rb") as f:
            self.data = tomllib.load(f)

    def get_versions(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for table_name, table in self.data["pkg"].items():
                if "api_interface" in table:
                    api_interface = table["api_interface"]
                    if api_interface == "Github":
                        repo = table["Github"]["repo"]
                        github = Github(repo)
                        future = executor.submit(self.gh_get_version_and_update_data, table_name, github.get_latest_version(), table["PKGBUILD"]["pkgrel"])
                        futures.append(future)
                    elif api_interface == "AUR":
                        aur_id = table["AUR"]["id"]
                        aur = Aur(table_name, aur_id)
                        future = executor.submit(self._get_version_and_update_data, table_name, aur.get_latest_version())
                        futures.append(future)
            concurrent.futures.wait(futures)
        return dumps(self.data, indent=2)

    def _get_version_and_update_data(self, table_name, version):
        self.data["pkg"][table_name]["Version"] = version["Version"]
        self.data["pkg"][table_name]["URLPath"] = version["URLPath"]


    def gh_get_version_and_update_data(self, table_name, version, pkgrel):
        self.data["pkg"][table_name]["Version"] = f"{version}-{pkgrel}"
        self.data["pkg"][table_name]["PKGBUILD"]["version"] = version
