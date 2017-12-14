# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from modgrammar import *
grammar_whitespace_mode = 'optional'


class PrintableCharacter(Grammar):
    grammar = (WORD('"A-Za-z', restchars='a-zA-Z0-9-\s\t\n\.():,\'/;'))


class Unmapped(Grammar):
    grammar = (WORD('A-Za-z', restchars='a-zA-Z0-9\-:/',
                    fullmatch=True, escapes=True), L(';'))


class Name(Grammar):
    grammar = (WORD("A-Za-z0-9", restchars='a-zA-Z0-9\-.',
                    fullmatch=True, escapes=True))


class NameInQuotes(Grammar):
    grammar = (WORD('"A-Za-z0-9', restchars='a-zA-Z0-9\-",.',
                    fullmatch=True, escapes=True))


class Description(Grammar):
    grammar = (L("description"),  WORD('"A-Za-z', restchars='![\x23-\x3A][\x3C-\x7E]\s\t\n;',
                                       fullmatch=True, escapes=True), L('"'), L(';'))


class Description2(Grammar):
    grammar = (L("description"),  WORD(
        '"A-Za-z', restchars='![\x23-\x3A][\x3C-\x7E]\s\t\n;', fullmatch=True, escapes=True), L('"'), L(';'))


class Key(Grammar):
    grammar = (L('key'), WORD('"a-z', restchars='a-zA-Z0-9\- "',
                              fullmatch=True, escapes=True), WORD(';'))


class NameWithCaps(Grammar):
    grammar = (WORD('A-Za-z', restchars='a-zA-Z0-9',
                    fullmatch=True, escapes=True))
