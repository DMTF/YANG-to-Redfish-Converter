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
from yang.feature import *
from yang.rpc import *
from yang.reference import *
from yang.identity import *
from yang.deviation import *
from yang.anyxml import *
grammar_whitespace_mode = 'optional'


class YangVersion(Grammar):
    grammar = (L("yang-version"), WORD('"0-9', restchars='0-9"',
                                       fullmatch=True, escapes=True), L(';'))


class Namespace(Grammar):
    grammar = (L("namespace"),  WORD(
        '"a-z', restchars='a-zA-Z0-9:/\-\."', fullmatch=True, escapes=True), L(';'))


class Organization(Grammar):
    #grammar = (L("organization"), L('"'), WORD("A-Za-z", restchars='a-zA-Z0-9:/-\.'), WORD('"'), WORD(';'))
    #grammar = (L("organization"), WORD('"A-Za-z', restchars='a-zA-Z0-9:-\s\t\n\."', fullmatch=True, escapes=True),  L(';'))
    grammar = (L("organization"), WORD(
        '"A-Za-z', restchars='[\x20-\x3A][\x3C-\x7E]\s\t\n"', fullmatch=True, escapes=True),  L(';'))


class Contact(Grammar):
    grammar = (L('contact'), WORD(
        '"A-Za-z', restchars='[\x20-\x3A][\x3C-\x7E]\s\t\n"', fullmatch=True, escapes=True), L(';'))

# TODO: Revision grammar has to be fixed -


class RevisionGrammar(Grammar):
    grammar = (L('revision'), OR(Name, NameInQuotes), OR(
        (OPENBRACE,
        REPEAT(
         Description |
         ReferenceGrammar, min=0),
         CLOSEBRACE)
        ,  L(';')))


class Prefix(Grammar):
    grammar = (L("prefix"), WORD(
        '"a-z', restchars='a-zA-Z"', fullmatch=True), L(';'))


class ModuleKeyword(Grammar):
    grammar = (L("module"))


class SubmoduleKeyword(Grammar):
    grammar = (L("submodule"))


class SubmoduleGrammar(Grammar):
    grammar = (SubmoduleKeyword,
               Name,
               OPENBRACE,
               REPEAT(Namespace | AnyXML | YangVersion | Prefix | Import | Include |
                      Organization | Contact | Description | RevisionGrammar, min=0),
               REPEAT(Augment | Grouping | Identity | ContainerGrammar | ChoiceGrammar |
                      RpcGrammar | Feature | TypedefGrammar | Deviation | Notification, min=0),
               CLOSEBRACE)


class ModuleGrammar(Grammar):
    grammar = (ModuleKeyword,
               Name,
               OPENBRACE,
               REPEAT(SubmoduleGrammar |  Namespace | AnyXML | YangVersion | Prefix | Import | Include | Organization | Contact | Description | RevisionGrammar | ReferenceGrammar, min=0),
               REPEAT(Augment | Grouping | Identity | ContainerGrammar | ChoiceGrammar |
                      RpcGrammar | Feature | TypedefGrammar | Deviation | Notification, min=0),
               CLOSEBRACE)
