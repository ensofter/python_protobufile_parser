import sys

from pyparsing import ParseResults

from parser import IParser, ProtoParser


class ProtoReader:

    def _read_proto(self, path_to_proto: str) -> str:
        with open(path_to_proto, 'r') as my_proto:
            proto_body = my_proto.read()
        return proto_body


class ProtoUtils:

    def _get_protofile_name(self, path_to_proto: str) -> str:
        proto_name = path_to_proto.split('/')[-1].removesuffix('.proto')
        if '-' in proto_name:
            proto_name = proto_name.replace('-', '_')
        return proto_name


class ProtoInfo(ProtoReader, ProtoUtils):

    def __init__(self, parser: IParser, path_to_proto: str, py_cli_package_name: str):
        self._proto_body = self._read_proto(path_to_proto)
        self._service_name: ParseResults = parser.service_name(self._proto_body)
        self._package: ParseResults = parser.package_directive(self._proto_body)
        self._imports: ParseResults = parser.import_directives(self._proto_body)
        self._handlers: ParseResults = parser.service_handlers(self._proto_body)
        self._path_to_proto = path_to_proto
        self._clear_proto_name = self._get_protofile_name(self._path_to_proto)
        self._py_cli_package_name = py_cli_package_name

    @property
    def service_name(self) -> ParseResults:
        return self._service_name

    @property
    def package(self) -> ParseResults:
        return self._package

    @property
    def imports(self) -> ParseResults:
        return self._imports

    @property
    def handlers(self) -> ParseResults:
        return self._handlers

    @property
    def path_to_proto(self) -> str:
        return self._path_to_proto

    @property
    def clear_proto_name(self) -> str:
        return self._clear_proto_name

    @property
    def py_cli_package_name(self) -> str:
        return self._py_cli_package_name


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
