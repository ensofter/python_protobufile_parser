from proto_info_builder import ProtoInfo


class ClientBuilder:

    def __init__(self, proto_info: ProtoInfo):
        self._proto_info = proto_info

    def _is_client(self) -> bool:
        return all([self._proto_info.handlers, self._proto_info.service_name])

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
        path_to_pb = self._proto_info.py_cli_package_name + "." + self._proto_info.path_to_proto.replace("/", ".").replace("-", "_").removesuffix(f'.{self._proto_info.clear_proto_name}.proto')
        imports_body = f"""from ozwhc.grpc_clients import BaseGrpc
from {path_to_pb} import {self._proto_info.clear_proto_name}_pb2, {self._proto_info.clear_proto_name}_pb2_grpc
from google.protobuf.empty_pb2 import Empty

"""
        return imports_body

    def generate_class(self):
        class_name_body = f"""
class {self._proto_info.uniq_client_name}(BaseGrpc):
    grpc_stub = {self._proto_info.clear_proto_name}_pb2_grpc.{self._proto_info.service_name}Stub
"""
        return class_name_body

    def generate_handlers(self):
        handlers_body = """"""
        for handler in self._proto_info.handlers:
            handler_name = self._handler_to_snake_case(handler)
            # проверка на наличие пустых реквестов и респонсов
            if 'google.protobuf.Empty' in handler['Request']:
                handlers_body += f"""
    def {handler_name}(self, request=Empty(), **kwargs) -> """
            else:
                handlers_body += f"""
    def {handler_name}(self, request: {self._proto_info.clear_proto_name}_pb2.{handler['Request']}, **kwargs) -> """

            if 'google.protobuf.Empty' in handler['Response']:
                handlers_body += f"""Empty():"""
            else:
                handlers_body += f"""{self._proto_info.clear_proto_name}_pb2.{handler['Response']}:"""

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

            path_to_package_file = f'{self._proto_info.py_cli_package_name}_setup/{self._proto_info.py_cli_package_name}/{self._proto_info.path_to_proto.replace("-", "_").removesuffix(f"{self._proto_info.clear_proto_name}.proto")}'
            with open(f"{path_to_package_file}__init__.py", "w") as file:
                file.write(init_body)
        else:
            print("Это протник с константами и для него не нужен клиент")


