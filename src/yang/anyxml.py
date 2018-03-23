# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

from modgrammar import *
from yang.brace import *
from yang.feature import *
grammar_whitespace_mode = 'optional'


class AnyXMLName(Grammar):
    grammar = (WORD('"a-zA-Z0-9', restchars='a-zA-Z0-9&"',
                    fullmatch=True, escapes=True))


class AnyXML(Grammar):
    grammar = (L('anyxml'), AnyXMLName, OPENBRACE,
               REPEAT(IfFeature), CLOSEBRACE)
