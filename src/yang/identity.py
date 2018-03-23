# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

from modgrammar import *
from yang.name import *
from yang.linkage import *
from yang.brace import *
from yang.enumtypes import EnumerationGrammar, EnumItemTypeA, EnumItemTypeB
from yang.localtypes import *
from yang.reference import *


grammar_whitespace_mode = 'optional'


class Identity(Grammar):
    grammar = (L('identity'), Name, OPENBRACE,
               REPEAT(Base | Description | Status | ReferenceGrammar, min=0),
               CLOSEBRACE)
