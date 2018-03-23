# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

from modgrammar import *
from yang.name import *
from yang.linkage import *
from yang.brace import *
from yang.enumtypes import EnumerationGrammar, EnumItemTypeA, EnumItemTypeB

grammar_whitespace_mode = 'optional'


class Base(Grammar):
    grammar = (L('base'), WORD('"a-zA-Z0-9', restchars='a-zA-Z0-9:\.\-"',
                               fullmatch=True, escapes=True), L(';'))


class Bit(Grammar):
    grammar = (L('bit'), WORD('"a-zA-Z0-9', restchars='a-zA-Z0-9:\."'), L(';'))


class Length(Grammar):
    grammar = (L('length'), WORD(
        '"a-zA-Z0-9', restchars='a-zA-Z0-9:\."', fullmatch=True, escapes=True), L(';'))


class Path(Grammar):
    grammar = (L('path'), WORD('"a-zA-Z0-9', restchars='a-zA-Z0-9:\.:/"-',
                               fullmatch=True, escapes=True), L(';'))


class Pattern(Grammar):
    grammar = (L('pattern'), WORD(
        '"a-zA-Z0-9', restchars='a-zA-Z0-9:\."', fullmatch=True, escapes=True), L(';'))


class Min(Grammar):
    grammar = (L('min'), WORD('"-a-zA-Z0-9+', restchars='a-zA-Z0-9:\.|\-\s\t"',
                              fullmatch=True, escapes=True), L(';'))


class Max(Grammar):
    grammar = (L('max'), WORD('"-a-zA-Z0-9+', restchars='a-zA-Z0-9:\.|\-\s\t"',
                              fullmatch=True, escapes=True), L(';'))


class OrderedBy(Grammar):
    grammar = (L('ordered-by'), WORD('"a-zA-Z0-9',
                                     restchars='a-zA-Z0-9:\."', fullmatch=True, escapes=True), L(';'))


class Range(Grammar):
    grammar = (L('range'), WORD('"-a-zA-Z0-9+',
                                restchars='a-zA-Z0-9:\.|\-\s\t"', fullmatch=True, escapes=True), L(';'))


class Status(Grammar):
    grammar = (L('status'), WORD('"a-zA-Z0-9+\-',
                                 restchars='a-zA-Z0-9:\.|\-\s\t"-', fullmatch=True, escapes=True), L(';'))


class SimpleType(Grammar):
    grammar = (WORD('"a-z', restchars='a-zA-Z0-9:\-"',
                    fullmatch=True, escapes=True), L(';'))


class SimpleTypeWithMetadata(Grammar):
    grammar = (
        WORD('"a-z', restchars='a-zA-Z0-9:\-"', fullmatch=True, escapes=True),
        OPENBRACE,
        REPEAT(Base | Bit | Length | Path | Pattern | Range | Min | Max),
        CLOSEBRACE
    )


class MinElements(Grammar):
    grammar = (L('min-elements'), WORD('"0-9',
                                       restchars='0-9"', fullmatch=True), L(';'))


class MaxElements(Grammar):
    grammar = (L('max-elements'), WORD('"0-9',
                                       restchars='0-9"', fullmatch=True), L(';'))


class Type(Grammar):
    #grammar = (L("type"), WORD('"a-z', restchars='a-z0-9:\-"', fullmatch=True, escapes=True), L(';'))
    grammar = (L("type"), OR(SimpleTypeWithMetadata,
                             SimpleType, EnumerationGrammar))
    #grammar = (L("type"), OR((SimpleType, L(';')), EnumerationGrammar))


class Units(Grammar):
    grammar = (L("units"), WORD('"a-z', restchars='a-z:"/',
                                fullmatch=True, escapes=True), L(';'))


class Default(Grammar):
    grammar = (L("default"), WORD(
        '"a-zA-Z0-9', restchars='a-zA-Z0-9"\-', fullmatch=True, escapes=True), L(';'))


class Config(Grammar):
    grammar = (L('config'), L('true') | L('"true"')
               | L('false') | L('"false"'), L(';'))


class Mandatory(Grammar):
    grammar = (L('mandatory'), L('true') | L('"true"')
               | L('false') | L('"false"'), L(';'))
