import os

from generator import YamlReader


class TestReadMimirYaml:

    def test_read_mimir_yaml(self):
        path_to_mimir = '../mimir.yaml'
        fp = open(path_to_mimir, 'w')
        fp.write('proto_paths:\n    - proto_files')
        fp.close()

        yaml_reader = YamlReader()
        proto_paths = yaml_reader._read_mimir_yaml(path_to_mimir)

        assert proto_paths == ['proto_files']

        os.remove(path_to_mimir)