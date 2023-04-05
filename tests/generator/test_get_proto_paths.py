import os

from generator import ProtoGenerator


class TestGetProtoPaths:

    def test_get_proto_paths(self):
        path_to_mimir = '../mimir.yaml'
        fp = open(path_to_mimir, 'w')
        fp.write('proto_paths:\n\t- proto_files')
        fp.close()

        proto_generator = ProtoGenerator()
        proto_paths = proto_generator.get_proto_paths(path_to_mimir)
        print("!!!", proto_paths)

        os.remove(path_to_mimir)