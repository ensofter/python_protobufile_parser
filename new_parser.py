import sys
from abc import ABC, abstractmethod

from pyparsing import Word, alphas, alphanums, Suppress, Optional, delimited_list, Keyword, restOfLine, \
    quoted_string, ParseResults, Literal, LineStart
from pyparsing.core import ParserElement


IDENT = Word(alphas + "_", alphanums + "_").setName("identifier")
LPAR = Suppress('(')
RPAR = Suppress(')')
EQ = Suppress('=')
SEMI = Suppress(';')
RPC_ = Keyword('rpc')
RETURNS_ = Keyword('returns')
SERVICE_ = Literal('service')
STREAM_ = Keyword('stream')
PACKAGE_ = Keyword('package')
IMPORT_ = Keyword('import')
COMMENT = '//' + restOfLine


class ProtoReader:

    def read_proto(self, path_to_proto: str):
        with open(path_to_proto, 'r') as my_proto:
            proto_body = my_proto.read()
        return proto_body


class IParser(ABC):

    @abstractmethod
    def package_directive(self):
        pass

    @abstractmethod
    def import_directives(self):
        pass

    @abstractmethod
    def service_name(self):
        pass

    @abstractmethod
    def service_handlers(self):
        pass

    def parse(self, parser_definition: ParserElement, proto_body: str):
        parser_definition.ignore(COMMENT)
        return parser_definition.search_string(proto_body)


class Parser(IParser, ProtoReader):

    def __init__(self, path_to_proto: str):
        self.proto_body = self.read_proto(path_to_proto)

    def package_directive(self) -> ParseResults:
        """ Парсим директиву package. """
        package_directive = (
                PACKAGE_
                - delimited_list(IDENT, '.', combine=True)('PackageString')
                + SEMI
        )
        if result_of_parsing := self.parse(package_directive, self.proto_body):
            return result_of_parsing[0]['PackageString']
        return result_of_parsing

    def import_directives(self) -> ParseResults:
        """ Парсим импорты внутри протника. """
        import_directives = (
                IMPORT_ - quoted_string('importPath') + SEMI
        )
        return self.parse(import_directives, self.proto_body)

    def service_name(self) -> ParseResults:
        """ Парсим имя сервиса внутри протника. """
        service_name = (
                LineStart() + SERVICE_
                - IDENT('serviceName')
        )
        if result_of_parsing := self.parse(service_name, self.proto_body):
            return result_of_parsing[0]['serviceName']
        return result_of_parsing

    def service_handlers(self) -> ParseResults:
        """ Парсим всю директиву service. """
        method_defn = (
                RPC_
                + IDENT("methodName")
                + LPAR
                + (Optional(STREAM_)('stream') + delimited_list(IDENT, '.', combine=True)("Request"))
                + RPAR
                + RETURNS_
                + LPAR
                + (Optional(STREAM_)('stream') + delimited_list(IDENT, '.', combine=True)("Response"))
                + RPAR
        )
        return self.parse(method_defn, self.proto_body)


class ParsedData:
    def __init__(self, parser: IParser):
        self._service_name: ParseResults = parser.service_name()
        self._package: ParseResults = parser.package_directive()
        self._imports: ParseResults = parser.import_directives()
        self._handlers: ParseResults = parser.service_handlers()

    @property
    def service_name(self):
        return self._service_name

    @property
    def package(self):
        return self._package

    @property
    def imports(self):
        return self._imports

    @property
    def handlers(self):
        return self._handlers


if __name__ == '__main__':
    proto_path = sys.argv[1]
    parser = Parser(proto_path)
    parsed_data = ParsedData(parser)
    print(parsed_data.service_name)
    print(parsed_data.package)
    print(parsed_data.imports)
    print(parsed_data.handlers)


