import requests

class Aur:
    def __init__(self, pkg_name, aur_id):
        self.pkg_name = pkg_name
        self.aur_id = aur_id
        self.api_url = f"https://aur.archlinux.org/rpc/v5/search/{self.pkg_name}?by=name"

    def get_latest_version(self):
        response = requests.get(self.api_url)
        if not response.ok:
            return None
        data = response.json()
        for result in data["results"]:
            if result["ID"] == self.aur_id:
                version = {
                    "Version": result["Version"],
                    "URLPath": f"https://aur.archlinux.org{result['URLPath']}"
                }
                return version
        return None
