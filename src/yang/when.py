# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from modgrammar import *
from yang.brace import *
from yang.name import *
from yang.localtypes import *
from yang.feature import *

grammar_whitespace_mode = 'optional'


class WhenName(Grammar):
    grammar = (WORD('a-zA-Z/"', restchars='!()[\x23-\x3A][\x3C-\x7E]\s\t\n"',
                    fullmatch=True, escapes=True))


class When(Grammar):
    grammar = (L('when'), WhenName, L(';'))
