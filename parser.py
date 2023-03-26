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


class IParser(ABC):

    @abstractmethod
    def package_directive(self, proto_body: str):
        pass

    @abstractmethod
    def import_directives(self, proto_body: str):
        pass

    @abstractmethod
    def service_name(self, proto_body: str):
        pass

    @abstractmethod
    def service_handlers(self, proto_body: str):
        pass

    def parse(self, parser_definition: ParserElement, proto_body: str):
        parser_definition.ignore(COMMENT)
        return parser_definition.search_string(proto_body)


class ProtoParser(IParser):

    def package_directive(self, proto_body: str) -> ParseResults:
        """ Парсим директиву package. """
        package_directive = (
                PACKAGE_
                - delimited_list(IDENT, '.', combine=True)('PackageString')
                + SEMI
        )
        if result_of_parsing := self.parse(package_directive, proto_body):
            return result_of_parsing[0]['PackageString']
        return result_of_parsing

    def import_directives(self, proto_body: str) -> ParseResults:
        """ Парсим импорты внутри протника. """
        import_directives = (
                IMPORT_ - quoted_string('importPath') + SEMI
        )
        return self.parse(import_directives, proto_body)

    def service_name(self, proto_body: str) -> ParseResults:
        """ Парсим имя сервиса внутри протника. """
        service_name = (
                LineStart() + SERVICE_
                - IDENT('serviceName')
        )
        if result_of_parsing := self.parse(service_name, proto_body):
            return result_of_parsing[0]['serviceName']
        return result_of_parsing

    def service_handlers(self, proto_body: str) -> ParseResults:
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
        return self.parse(method_defn, proto_body)


if __name__ == '__main__':
    proto_path = sys.argv[1]
    with open(proto_path, 'r') as proto_file:
        proto_body = proto_file.read()

    parser = ProtoParser()
    package = parser.package_directive(proto_body)
    imports = parser.import_directives(proto_body)
    service_name = parser.service_name(proto_body)
    handlers = parser.service_handlers(proto_body)

    print(package)
    print(imports)
    print(service_name)
    print(handlers)



