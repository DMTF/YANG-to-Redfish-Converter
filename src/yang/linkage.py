# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from modgrammar import *
grammar_whitespace_mode = 'optional'


class Prefix(Grammar):
    grammar = (L("{"), L("prefix"), WORD(
        '"a-z', restchars='a-zA-Z\-."', escapes=True, fullmatch=True), L(";"), L("}"))


class Import(Grammar):
    grammar = (L("import"), WORD('a-z', restchars='a-zA-Z\-',
                                 fullmatch=True, escapes=True), OR(Prefix | L(";")))


class Include(Grammar):
    grammar = (L("include"), WORD('0-9a-zA-Z', restchars='0-9a-zA-Z\-',
                                 fullmatch=True, escapes=True), L(";"))

