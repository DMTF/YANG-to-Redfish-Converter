# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

from modgrammar import *
from yang.brace import *
from yang.name import *
from yang.localtypes import *
from yang.feature import *
from yang.presence import *
from yang.reference import *

grammar_whitespace_mode = 'optional'


class Refine(Grammar):
    grammar = (L('refine'), WORD('a-z', restchars='A-Z', fullmatch=True, escapes=True),
               OPENBRACE,
               REPEAT(Default | Config | Mandatory | Description |
                      Reference | Presence | MinElements | MaxElements, min=0),
               CLOSEBRACE
               )
