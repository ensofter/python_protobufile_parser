import sys

from pyparsing import Word, alphas, alphanums, Regex, Suppress, Optional, \
    delimited_list, Keyword, restOfLine, quoted_string, ParseResults, \
    Literal, LineStart


ident = Word(alphas + "_", alphanums + "_").setName("identifier")
integer = Regex(r"[+-]?\d+")

LBRACE = Suppress('{')
RBRACE = Suppress('}')
LBRACK = Suppress('[')
RBRACK = Suppress(']')
LPAR = Suppress('(')
RPAR = Suppress(')')
EQ = Suppress('=')
SEMI = Suppress(';')
COLON = Suppress(':')
RPC_ = Keyword('rpc')
RETURNS_ = Keyword('returns')
SERVICE_ = Literal('service')
OPTION_ = Keyword('option')
BODY_ = Keyword('body')
STREAM_ = Keyword('stream')
PACKAGE_ = Keyword('package')
IMPORT_ = Keyword('import')
TRUE_ = Keyword('true')
COMMENT = '//' + restOfLine


class Parser:

    def __init__(self, proto_file: str):
        self.proto_file = proto_file

    def parsing_package_directive(self) -> str:
        """ Парсим директиву package. """
        package_directive = (
                PACKAGE_
                - delimited_list(ident, '.', combine=True)('PackageString')
                + SEMI
        )
        package_directive.ignore(COMMENT)
        result_of_parsing = package_directive.search_string(self.proto_file)
        return result_of_parsing[0].as_dict()['PackageString']

    def parsing_import_directives(self) -> ParseResults:
        """ Парсим импорты внутри протника. """
        import_directives = (
                IMPORT_ - quoted_string('importPath') + SEMI
        )
        import_directives.ignore(COMMENT)
        result_of_parsing = import_directives.search_string(self.proto_file)
        return result_of_parsing

    def parsing_service_name(self) -> str:
        """ Парсим имя сервиса внутри протника. """
        service_name = (
                LineStart() + SERVICE_
                - ident('serviceName')
        )
        service_name.ignore(COMMENT)
        if result_of_parsing := service_name.search_string(self.proto_file):
            return result_of_parsing[0].as_dict()['serviceName']
        return ''

    def parsing_service_handles(self) -> ParseResults:
        """ Парсим всю директиву service. """
        method_defn = (
                RPC_
                - ident("methodName")
                + LPAR
                + (Optional(STREAM_)('stream') + delimited_list(ident, '.', combine=True)("Request"))
                + RPAR
                + RETURNS_
                + LPAR
                + (Optional(STREAM_)('stream') + delimited_list(ident, '.', combine=True)("Response"))
                + RPAR
        )
        method_defn.ignore(COMMENT)
        result_of_parsing = method_defn.search_string(self.proto_file)

        return result_of_parsing


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as my_file:
        proto_body = my_file.read()
        parser = Parser(proto_body)
        result = parser.parsing_service_handles()
        print('!!!', result)


