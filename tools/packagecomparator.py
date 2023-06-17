import json
import packaging.version as pv

class PackageComparator:
    def __init__(self, db_json, package_json):
        self.db_json = json.loads(db_json)
        self.package_json = json.loads(package_json)

    def compare(self):
        new_data = {}
        for pkg_name, pkg_data in self.package_json['pkg'].items():
            db_pkg_data = next((v for k, v in self.db_json.items() if v['name'] == pkg_name), None)
            if db_pkg_data is None:
                pkg_data['isnew'] = True
                new_data[pkg_name] = pkg_data
            else:
                db_version = pv.parse(db_pkg_data['version'])
                pkg_version = pv.parse(pkg_data['Version'])
                if pkg_version > db_version:
                    pkg_data['isnew'] = False
                    pkg_data['s3filename'] = db_pkg_data['filename']
                    new_data[pkg_name] = pkg_data
        if new_data == {}:
            return None
        else:
            return json.dumps({'pkg': new_data}, indent=2)
