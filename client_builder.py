from abc import ABC, abstractmethod
from parser import ProtoParser, ProtoInfo


class ClientBuilder:

    def __init__(self, parsed_data: ProtoInfo):
        self._parsed_data = parsed_data

    def _is_client(self) -> bool:
        return all([self._parsed_data.handlers, self._parsed_data.service_name])

    def _uniq_client_class_name(self) -> str:
        package_directive = self._parsed_data.package.replace('_', '.').split('.')
        package_directive = ''.join(name.title() for name in package_directive)
        return str(package_directive + self._parsed_data.service_name)

    def _handler_to_snake_case(self, handler_name: str) -> str:
        name = handler_name['methodName']
        if 'ID' in name:
            name = name.replace('ID', 'Id')
        func_method_name = name[0].lower()
        for i in name[1:]:
            if i.isupper():
                func_method_name += f'_{i.lower()}'
            else:
                func_method_name += i
        return func_method_name

    def generate_imports(self):
        path_to_pb = self._parsed_data.py_cli_package_name + "." + self._parsed_data.path_to_proto.replace("/", ".").replace("-", "_").removesuffix(f'.{self._parsed_data.clear_proto_name}.proto')
        imports_body = f"""from ozwhc.grpc_clients import BaseGrpc
from {path_to_pb} import {self._parsed_data.clear_proto_name}_pb2, {self._parsed_data.clear_proto_name}_pb2_grpc
from google.protobuf.empty_pb2 import Empty

"""
        return imports_body

    def generate_class(self):
        uniq_class_name = self._uniq_client_class_name()
        class_name_body = f"""
class {uniq_class_name}(BaseGrpc):
    grpc_stub = {self._parsed_data.clear_proto_name}_pb2_grpc.{self._parsed_data.service_name}Stub
"""
        return class_name_body

    def generate_handlers(self):
        handlers_body = """"""
        for handler in self._parsed_data.handlers:
            handler_name = self._handler_to_snake_case(handler)
            # проверка на наличие пустых реквестов и респонсов
            if 'google.protobuf.Empty' in handler['Request']:
                handlers_body += f"""
    def {handler_name}(self, request=Empty(), **kwargs) -> """
            else:
                handlers_body += f"""
    def {handler_name}(self, request: {self._parsed_data.clear_proto_name}_pb2.{handler['Request']}, **kwargs) -> """

            if 'google.protobuf.Empty' in handler['Response']:
                handlers_body += f"""Empty():"""
            else:
                handlers_body += f"""{self._parsed_data.clear_proto_name}_pb2.{handler['Response']}:"""

            # проверка на наличие стримов в методе
            if 'stream' in handler:
                handlers_body += f"""
        return self._grpc_stream(request=request, request_method=self.stub.{handler['methodName']}, **kwargs)
        """
            else:
                handlers_body += f"""
        return self._grpc_request(request=request, request_method=self.stub.{handler['methodName']}, **kwargs)
        """
        return handlers_body

    def generate_client_for_proto(self):
        if self._is_client():
            init_body = """"""
            init_body += self.generate_imports()
            init_body += self.generate_class()
            init_body += self.generate_handlers()

            path_to_package_file = f'{self._parsed_data.py_cli_package_name}_setup/{self._parsed_data.py_cli_package_name}/{self._parsed_data.path_to_proto.replace("-", "_").removesuffix(f"{self._parsed_data.clear_proto_name}.proto")}'
            with open(f"{path_to_package_file}__init__.py", "w") as file:
                file.write(init_body)
        else:
            print("Это протник с константами и для него не нужен клиент")


