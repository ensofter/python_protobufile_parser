from client_builder import ClientBuilder
from generator import ProtoGenerator
from parser import ProtoParser
from proto_info_builder import ProtoInfo

if __name__ == '__main__':
    py_cli_package_name: str = 'qa_whc_api_supply_grpc_client'

    proto_generator = ProtoGenerator()
    proto_paths: list = proto_generator.get_proto_paths()
    proto_generator.create_environment_for_package(py_cli_package_name, proto_paths)

    for path_to_proto in proto_paths:
        parser = ProtoParser()
        proto_info = ProtoInfo(parser, path_to_proto, py_cli_package_name)

        proto_generator.get_external_dependencies(proto_info.imports)
        proto_generator.generate_pb_files(py_cli_package_name, proto_info.full_path_to_proto, proto_info.is_service)

        client_builder = ClientBuilder(proto_info)
        client_builder.generate_client_for_proto()
