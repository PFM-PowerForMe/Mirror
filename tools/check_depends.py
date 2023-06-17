import json
import logging
import subprocess

class CheckDepends:
    def __init__(self, logger: logging.Logger, str_package_data: str, search_db_data: str):
        self.str_package_data = str_package_data
        self.search_db_data = search_db_data
        self.logger = logger
        pass

    def check_depends_in_mirror(self) -> str:
        # 检查"depends_in_mirror"为True的包的依赖是否在镜像中
        flag = 0
        new_package_data = {}
        package_data = json.loads(self.str_package_data)
        search_db_data = json.loads(self.search_db_data)
        for tablename, table in package_data["pkg"].items():
            if "depends_in_mirror" in table:
                if table["depends_in_mirror"] == True:
                    if "depends" in table:
                        for depend in table["depends"]:
                            if depend not in search_db_data["pkg"]:
                                self.logger.info(f"Package {tablename} depends on {depend}, but {depend} not in mirror")
                                continue
                            else:
                                flag = +1
                                new_package_data[tablename] = table
                    else:
                        self.logger.info(f"Package {tablename} depends on nothing, but depends_in_mirror is True")
                        continue
                else:
                    new_package_data[tablename] = table
            else:
                new_package_data[tablename] = table
        if flag != 0:
            try:
                subprocess.run(f'sudo cat /pacman.conf >> /etc/pacman.conf && sudo pacman -Syy', check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                self.logger.error(f'refresh pacman failed with exception: {e}')
                self.logger.error(f'refresh pacman failed with stdeer: {e.stderr.decode()}')
                exit(1)

        return json.dumps(new_package_data, indent=2)
