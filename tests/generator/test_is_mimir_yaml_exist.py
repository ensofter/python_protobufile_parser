import os

import constants
from generator import ProtoGenerator


class TestIsMimirYamlExist:

    def test_is_mimir_yaml_exist(self):
        fp = open(constants.MIMIR_YAML, 'w')
        fp.close()

        proto_generator = ProtoGenerator()
        is_exist = proto_generator._is_mimir_yaml_exist(constants.MIMIR_YAML)
        assert is_exist

        os.remove(constants.MIMIR_YAML)

    def test_is_mimir_yaml_not_exist(self):
        proto_generator = ProtoGenerator()
        is_exist = proto_generator._is_mimir_yaml_exist(constants.MIMIR_YAML)
        assert not is_exist
