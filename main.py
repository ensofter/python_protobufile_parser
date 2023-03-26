import sys

from parser import ProtoParser, ProtoInfo
from client import ClientBuilder


if __name__ == '__main__':
    py_cli_package_name = 'qa_whc_api_supply_grpc_client'
    path_to_proto = sys.argv[1]

    parser = ProtoParser()
    proto_info = ProtoInfo(parser, path_to_proto, py_cli_package_name)
    print(proto_info.service_name)
    print(proto_info.package)
    print(proto_info.imports)
    print(proto_info.handlers)
    print(proto_info.path_to_proto)
    print(proto_info.clear_proto_name)
    print(proto_info.py_cli_package_name)

    client_builder = ClientBuilder(proto_info)
    client_builder.generate_client_for_proto()
