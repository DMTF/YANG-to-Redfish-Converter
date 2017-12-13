# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from modgrammar import *
from yang.name import *
from yang.linkage import *
from yang.localtypes import *
from yang.brace import *
from yang.reference import *
from yang.comment import *

grammar_whitespace_mode = 'optional'


class TypedefKeyword(Grammar):
    grammar = (L('typedef'))


class TypedefGrammar(Grammar):
    grammar = (TypedefKeyword, 
               Name,
               OPENBRACE,
               Type,
               OPTIONAL(Description),
               OPTIONAL(ReferenceGrammar),
               CLOSEBRACE
               )
