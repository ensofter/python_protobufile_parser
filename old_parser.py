"""
Надо бы написать доку
"""
import sys
import glob

from pyparsing import (Word, alphas, alphanums, Regex, Suppress, Forward,
    Group, oneOf, ZeroOrMore, Optional, delimitedList, Keyword,
    restOfLine, quotedString, Dict, OneOrMore)

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

MESSAGE_ = Keyword('message')
REQUIRED_ = Keyword('required')
OPTIONAL_ = Keyword('optional')
REPEATED_ = Keyword('repeated')
ENUM_ = Keyword('enum')
EXTENSIONS_ = Keyword('extensions')
EXTENDS_ = Keyword('extends')
EXTEND_ = Keyword('extend')
TO_ = Keyword('to')
PACKAGE_ = Keyword('package')
SERVICE_ = Keyword('service')
RPC_ = Keyword('rpc')
RETURNS_ = Keyword('returns')
TRUE_ = Keyword('true')
FALSE_ = Keyword('falsee')
OPTION_ = Keyword('option')
IMPORT_ = Keyword('import')
SYNTAX_ = Keyword('syntax')
BODY_ = Keyword('body')
MAP_ = Keyword('map')
JSON_NAME_ = Keyword('json_name')

messageBody = Forward()

messageDefn = MESSAGE_ - ident("messageId") + LBRACE + messageBody('body') + RBRACE
mapSpec = '<' + oneOf('''int64 string''') + ',' + ident + '>'
typespec = oneOf("""double float int32 int64 uint32 uint64 sint32 sint64
                    fixed32 fixed64 sfixed32 sfixed64 bool string bytes
                    google.protobuf.Timestamp google.protobuf.Int32Value
                    google.protobuf.Int64Value google.protobuf.BoolValue""") | ident | mapSpec



# типа того {gt: 0, lte: 2000000}
value_in_figures = LBRACE + ident + COLON + integer + ',' + ident + COLON + integer + RBRACE
rvalue = integer | TRUE_ | FALSE_ | ident | value_in_figures

# Директива типа вот такой = (validate.rules).repeated.unique = true, Может быть
# больше одного через запятую
fieldDirectiveFirst = (
        LPAR
        + delimitedList(ident, '.', combine=True)
        + RPAR
        + '.'
        + delimitedList(ident, '.', combine=True)
        + EQ
        + rvalue
        + Optional(',')
    )

# Директива типа вот тако = json_name="item_id"
fieldDirectiveSecond = (
    JSON_NAME_
    + EQ
    + quotedString
    + Optional(',')
    )

directive_type = fieldDirectiveFirst | fieldDirectiveSecond

fieldDirective = (
    LBRACK
    + ZeroOrMore(directive_type)
    + RBRACK
)

fieldDefnPrefix = REQUIRED_ | OPTIONAL_ | REPEATED_ | MAP_

fieldDefn = (
    Optional(fieldDefnPrefix)
    + typespec("typespec")
    + ident("ident")
    + EQ
    + integer("fieldint")
    + ZeroOrMore(fieldDirective)
    + SEMI
)

enumDefn = (
    ENUM_("typespec")
    - ident('name')
    + LBRACE
    + Dict(ZeroOrMore( Group(ident + EQ + integer + SEMI)))('values')
    + RBRACE
)

extensionsDefn = EXTENSIONS_ - integer + TO_ + integer + SEMI

messageExtension = EXTEND_ - ident + LBRACE + messageBody + RBRACE

messageBody << Group(
    ZeroOrMore(
        Group(fieldDefn | enumDefn | messageDefn | extensionsDefn | messageExtension)
    )
)
rpc_method = Keyword('post') | Keyword('get')

optionBody = (
    rpc_method
    + COLON
    + quotedString("endpointString")
    + Optional(',')
    + Optional(
        BODY_
        + COLON
        + quotedString('*')
    )
)

optionDefn = (
    OPTION_
    + LPAR
    + delimitedList(ident, '.', combine=True)
    + RPAR
    + EQ
    + LBRACE
    + Group(optionBody)('option body')
    + RBRACE
    + SEMI
)

methodDefn = (
    RPC_
    - ident("methodName")
    + LPAR
    + ident("methodRequest")
    + RPAR
    + RETURNS_
    + LPAR
    + ident("methodReturn")
    + RPAR
    + Optional(
        LBRACE
        + Group(optionDefn)('option')
        + RBRACE
    )
    + Optional(SEMI)
)

serviceDefn = (
    SERVICE_
    - ident.setResultsName('serviceName')
    + LBRACE
    + ZeroOrMore(Group(methodDefn))('serviceMethods')
    + RBRACE
)

packageDirective = (
    PACKAGE_ - delimitedList(ident, '.', combine=True)('PackageString') + SEMI
)

comment = '//' + restOfLine

syntaxDefn = (
    SYNTAX_ + EQ - quotedString("syntaxString") + SEMI
)

importDirective = (
    IMPORT_ - quotedString("importFileSpec") + SEMI
)

optionDirective = (
    OPTION_ - ident("optionName") + EQ + quotedString("optionValue") + SEMI
)

topLevelStatement = Group(
    messageDefn
    | messageExtension
    | enumDefn
    | serviceDefn
    | importDirective
    | optionDirective
    | syntaxDefn
    | packageDirective
)

parser = ZeroOrMore(topLevelStatement)

parser.ignore(comment)

def imports_init(proto_name):
    imports = f"""from ozwhc.grpc_clients import BaseGrpc
import {proto_name}_pb2, {proto_name}_pb2_grpc

"""
    return imports

def class_init(proto_name, service_name):
    class_name = f"""
class {service_name}(BaseGrpc):
    grpc_stub = {protofile_name}_pb2_grpc.{service_name}Stub
"""
    return class_name

def change_method_name(name):
    func_method_name = name['methodName'][0].lower()
    for i in name['methodName'][1:]:
        if i.isupper():
            func_method_name += f'_{i.lower()}'
        else:
            func_method_name += i
    return func_method_name


def methods_init(all_methods):
    methods = """"""
    for method in all_methods:
        method_name = change_method_name(method)
        methods += f"""
    def {method_name}(self, request, **kwargs):
        return self._grpc_request(request=request, request_method=self.stub.{method['methodName']}, **kwargs)

"""
    return methods

def create_init_file(proto_name, service_name, methods):
    init_body = """"""
    init_body += imports_init(proto_name)
    init_body += class_init(proto_name, service_name)
    init_body += methods_init(methods)
    with open("__init__.py", "w") as file:
        file.write(init_body)


if __name__ == "__main__":

   with open(sys.argv[1], 'r') as my_file:
       proto_body = my_file.read().replace('\n', '')
       result = parser.parseString(proto_body)
       print("!!!", result)
