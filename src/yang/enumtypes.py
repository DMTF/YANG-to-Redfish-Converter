# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

from modgrammar import *
from yang.name import *
from yang.linkage import *
from yang.brace import *
from yang.reference import *
from yang.localtypes import *
grammar_whitespace_mode = 'optional'

class ValueKeyword(Grammar):
    grammar = (L('value'), WORD('"A-Za-z0-9', restchars='a-zA-Z0-9"', fullmatch=True, escapes=True), L(';'))

class EnumerationKeyword(Grammar):
    grammar = (L('enumeration'))


class EnumItemTypeA(Grammar):
    grammar = (
        L('enum'),
        NameInQuotes,
        OPENBRACE,
        REPEAT( ValueKeyword | Description |
            ReferenceGrammar
            # | Status
            , min = 0) ,
        CLOSEBRACE
    )


class EnumItemTypeB(Grammar):
    grammar = (
        L('enum'), NameInQuotes, L(';')
    )


class EnumerationGrammar(Grammar):
    grammar = (EnumerationKeyword, OPENBRACE, REPEAT(
        EnumItemTypeA | EnumItemTypeB, min=1), CLOSEBRACE)
