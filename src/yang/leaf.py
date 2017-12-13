# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from modgrammar import *
from yang.name import *
from yang.linkage import *
from yang.brace import *
from yang.localtypes import *
from yang.enumtypes import EnumerationGrammar, EnumItemTypeA, EnumItemTypeB
from yang.feature import *
from yang.reference import *
from yang.must import *

grammar_whitespace_mode = 'optional'


class LeafKeyword(Grammar):
    grammar = (L("leaf"))


class LeafListKeyword(Grammar):
    grammar = (L("leaf-list"))


class LeafGrammar(Grammar):
    grammar = (LeafKeyword, Name,
               OPENBRACE,
               OPTIONAL(IfFeature),
               REPEAT(ReferenceGrammar | Unmapped | Type | Description |
                      Units | Default | Config | Mandatory, min=0),
               # Type,
               #REPEAT(Description | Units | Default | Config, min=0),
               CLOSEBRACE)


class LeafListGrammar(Grammar):
    grammar = (LeafListKeyword, Name,
               OPENBRACE,
               REPEAT(OrderedBy | Type | Description | Units | ReferenceGrammar |
                      Default | Config | Mandatory | Must, min=0),
               # Type, #Type must be present
               #REPEAT(Description | Units | Default | Config, min=0),
               CLOSEBRACE)
