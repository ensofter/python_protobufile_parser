import glob
import os

from generator import ProtoGenerator


class TestGetProtoPaths:

    def test_get_proto_paths(self):
        path_to_mimir = 'mimir.yaml'
        fp = open(path_to_mimir, 'w')
        fp.write('proto_paths:\n    - proto_files')
        fp.close()

        expected_proto_paths: list = glob.glob(f"proto_files/**/*.proto", recursive=True)

        proto_generator = ProtoGenerator()
        proto_paths = proto_generator.get_proto_paths(path_to_mimir)

        assert len(proto_paths) == len(expected_proto_paths)
        assert sorted(proto_paths) == sorted(expected_proto_paths)

        os.remove(path_to_mimir)
