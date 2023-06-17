import requests
import re

class Github:
    def __init__(self, repo):
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{self.repo}/releases/latest"

    def get_latest_version(self):
        response = requests.get(self.api_url)
        response.raise_for_status()
        version_str = response.json()["tag_name"]
        match = re.search(r"\d+\.\d+\.\d+", version_str)
        if match:
            return match.group()
        return None
