# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

from modgrammar import *
from yang.brace import *
from yang.reference import *
from yang.localtypes import *
from yang.must import *
from yang.unique import *
from yang.name import *
grammar_whitespace_mode = 'optional'


class DeviateKeyword(Grammar):
    grammar = (L('deviate'))


class DeviateValue(Grammar):
    grammar = (L('add') | L('replace') | L('not-supported') | L('delete'))


class Deviate(Grammar):
    grammar = (L('deviate'),
               DeviateValue,
               OPENBRACE,
               (Config | Default | Mandatory | MinElements |
                MaxElements | Must | Type | Unique | Units),
               CLOSEBRACE
               )


class DeviationValue(Grammar):
    grammar = (WORD('a-zA-Z/', restchars='a-zA-Z/:\.'))


class Deviation(Grammar):
    grammar = (L('deviation'),
               DeviationValue,
               OPENBRACE,
               REPEAT(Deviate, min=0),  # REPEAT(SingleLineComment, min=0),
               OPTIONAL(ReferenceGrammar),  # REPEAT(SingleLineComment, min=0),
               CLOSEBRACE
               )
