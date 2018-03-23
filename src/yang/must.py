# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

from modgrammar import *
from yang.name import *
from yang.brace import *
from yang.reference import *
grammar_whitespace_mode = 'optional'


class ErrorMessage(Grammar):
    grammar = (L('error-message'), WORD('a-zA-Z"',
                                        restchars='a-zA-Z0-9\.()"/\'+\s\n\t,', fullmatch=True, escapes=True), L(';'))


class ErrorAppTag(Grammar):
    grammar = (L('error-app-tag'), WORD('a-zA-Z"',
                                        restchars='a-zA-Z0-9\.()"/\'+\s\n\t,', fullmatch=True, escapes=True), L(';'))


class MustName(Grammar):
    grammar = (WORD('a-zA-Z\'"', restchars='!()[\x23-\x3A][\x3C-\x7E]\s\t\n"',
                    fullmatch=True, escapes=True))


class Must(Grammar):
    grammar = (L('must'), MustName,
               OR(L(';'), (OPENBRACE,
               REPEAT(ErrorMessage | ErrorAppTag |
                      ReferenceGrammar | Description2, min=0),
               CLOSEBRACE)
            )
        )
