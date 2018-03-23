# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

from modgrammar import *
grammar_whitespace_mode = 'optional'


class ReferenceGrammar(Grammar):
    grammar = (L('reference'), WORD(
        '"A-Za-z', restchars='[\x20-\x3A][\x3C-\x7E]\s\t\n"', fullmatch=True, escapes=True), L(';'))
