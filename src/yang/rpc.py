# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from modgrammar import *
from yang.name import *
from yang.linkage import *
from yang.brace import *
from yang.leaf import *
from yang.localtypes import *
from yang.enumtypes import EnumerationGrammar, EnumItemTypeA, EnumItemTypeB
from yang.feature import *

grammar_whitespace_mode = 'optional'


class InputKeyword(Grammar):
    grammar = (L("input"))


class InputGrammar(Grammar):
    grammar = (InputKeyword, OPENBRACE, OPTIONAL(LeafGrammar), CLOSEBRACE)


class OutputKeyword(Grammar):
    grammar = (L("output"))


class OutputGrammar(Grammar):
    grammar = (OutputKeyword, OPENBRACE, OPTIONAL(LeafGrammar), CLOSEBRACE)


class RpcKeyword(Grammar):
    grammar = (L("rpc"))


class RpcGrammar(Grammar):
    grammar = (RpcKeyword, Name, OPENBRACE,
               OPTIONAL(Unmapped),
               OPTIONAL(Description),
               OPTIONAL(InputGrammar),
               OPTIONAL(OutputGrammar),
               CLOSEBRACE
               )
