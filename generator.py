import glob
import os
import shutil
import subprocess
import tarfile
from os.path import exists

import requests
import yaml
from pyparsing import ParseResults

import constants


class YamlReader:

    def _read_mimir_yaml(self, path_to_mimir: str) -> list:
        with open(path_to_mimir) as file:
            paths = yaml.safe_load(file)
        return paths['proto_paths']


class ProtoGenerator(YamlReader):

    def create_environment_for_package(self, package_name: str, proto_paths: list):
        os.makedirs(package_name, exist_ok=True)
        os.makedirs(f'{package_name}_setup', exist_ok=True)
        for path_to_proto in proto_paths:
            self.create_folder_and_copy_proto(package_name, path_to_proto)

    def get_proto_paths(self) -> list:
        if not exists(constants.PATH_TO_MIMIR):
            raise AssertionError('Файл mimir.yaml отсутствует. Возможно это C# сервис')
        proto_folders: list = self._read_mimir_yaml(constants.PATH_TO_MIMIR)
        paths: set = set()
        for folder in proto_folders:
            paths_to_proto_files: list = glob.glob(f"{folder}/**/*.proto", recursive=True)
            for path in paths_to_proto_files:
                paths.add(path)
        return list(paths)

    def create_folder_and_copy_proto(self, package_name: str, path_to_proto: str):
        dst = f"{package_name}/{path_to_proto}"
        dst_folder = os.path.dirname(dst)
        if not os.path.exists(dst_folder):
            os.makedirs(dst_folder)
        shutil.copy(path_to_proto, dst)

    def get_external_dependencies(self, proto_imports: ParseResults):
        if proto_imports:
            for import_path in proto_imports:
                external_proto = import_path['importPath'].replace('"', '')
                if external_proto not in constants.VENDORS_PROTO:
                    print(f'У протника имеется внешняя зависимость {external_proto}. '
                          'Добавьте ее в исключение или сформируйте пакет')
                    url = 'http://mimir.platform.prod.s.o3.ru/v1/vendor'
                    headers = {"Content-Type": "application/json", "x-o3-sample-trace": "true"}
                    data = {"dependencies":
                        [{
                            "import_path": f"{external_proto}",
                            "version": "master"
                        }]}
                    response = requests.post(url, headers=headers, json=data, stream=True)
                    if response.status_code == 200:
                        file = tarfile.open(fileobj=response.raw, mode="r|gz")
                        file.extractall(path="./vendor.pb")
                    else:
                        print(response.status_code)
                        print(response.content)

    def generate_pb_files(self, package_name: str, path_to_proto: str, is_service: bool):
        if is_service:
            cmd = f"python -m grpc_tools.protoc -I=.:vendor.pb --python_out=./{package_name}_setup/ --grpc_python_out=./{package_name}_setup/ ./{path_to_proto}"
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            out, err = p.communicate()
            if err:
                print('PROTOC ERROR: ', err)
        print(f'Это протник с константами {path_to_proto}, его не нужно генерировать')
