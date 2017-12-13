# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from modgrammar import *
from yang.name import *
from yang.localtypes import *
from yang.linkage import *
from yang.brace import *
from yang.container import *
from yang.typedef import *
grammar_whitespace_mode = 'optional'


class IfFeature(Grammar):
    grammar = (L('if-feature'), Name, L(';'))


class Feature(Grammar):
    grammar = (L('feature'),
               Name,
               OPENBRACE,
               REPEAT(IfFeature, min=0),
               Description,
               OPTIONAL(L('reference'), WORD(
                   '"A-Za-z', restchars='a-zA-Z0-9-\s\t\n.():,\'/"', fullmatch=True, escapes=True), L(';')),
               CLOSEBRACE
               )
