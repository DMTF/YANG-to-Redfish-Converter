# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from modgrammar import *
from yang.brace import *
from yang.reference import *
from yang.localtypes import *
from yang.name import *
grammar_whitespace_mode = 'optional'


class Argument(Grammar):
    grammar = (L('argument'), NameInQuotes, L(';'))


class Extension(Grammar):
    grammar = (L('extension'), Name,
               OPENBRACE,
               REPEAT(Description | Argument, min=0),
               CLOSEBRACE
               )
