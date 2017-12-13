# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from modgrammar import *
from yang.name import *
from yang.linkage import *
from yang.brace import *
from yang.rpc import *
from yang.leaf import *
from yang.reference import *
grammar_whitespace_mode = 'optional'


class Unique(Grammar):
    grammar = (L('unique'), WORD(
        '"a-zA-Z0-9', restchars='a-zA-Z0-9\s\t\n"\.', fullmatch=True, escapes=True), L(';'))
