# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from modgrammar import *
from yang.name import *
from yang.linkage import *
from yang.brace import *
from yang.rpc import *
from yang.leaf import *
from yang.reference import *
from yang.refine import *
from yang.unique import *
from yang.presence import *
from yang.comment import *
from yang.identity import *
from yang.localtypes import *
from yang.typedef import *
from yang.when import *
grammar_whitespace_mode = 'optional'


class GroupingKeyword(Grammar):
    grammar = (L('grouping'))


class Grouping(Grammar):
    grammar = (GroupingKeyword, Name, OPENBRACE,
               OPTIONAL(Description),
               REPEAT(REF('ContainerGrammar') | REF(
                   'LeafGrammar') | ReferenceGrammar | REF('ListGrammar'), min=0),
               CLOSEBRACE
               )


class ContainerKeyword(Grammar):
    grammar = (L("container"))


class ContainerGrammar(Grammar):
    grammar = (ContainerKeyword, Name, OPENBRACE,
               REPEAT(Config | ReferenceGrammar | IfFeature | Unmapped | Presence | Description
                      | Identity | OrderedBy | REF("ContainerGrammar") | REF("ListGrammar") | LeafGrammar | LeafListGrammar | REF("ChoiceGrammar") | RpcGrammar
                      | REF("Uses"), min=0),
               CLOSEBRACE, OPTIONAL(SingleLineComment)
               )


class CaseKeyword(Grammar):
    grammar = (L("case"))


class CaseGrammar(Grammar):
    grammar = (CaseKeyword, Name,
               OPENBRACE,
               OPTIONAL(Description),
               OPTIONAL(IfFeature),
               REPEAT(LeafGrammar, min=0),
               REPEAT(REF("ContainerGrammar"), min=0),
               # REPEAT( ContainerGrammar | LeafGrammar , min=0),
               CLOSEBRACE
               )


class ChoiceKeyword(Grammar):
    grammar = (L("choice"))


class ChoiceGrammar(Grammar):
    grammar = (ChoiceKeyword,  Name,
               OPENBRACE,
               REPEAT(Description | CaseGrammar | LeafGrammar | Default | # do we care about default?
                      Mandatory | REF('ContainerGrammar'), min=0),
               CLOSEBRACE, OPTIONAL(SingleLineComment)
               )


class InputKeyword(Grammar):
    grammar = (L("input"))


class InputGrammar(Grammar):
    grammar = (InputKeyword, Name, OPENBRACE,
               REPEAT(Key | Description, min= 0),
               REPEAT (LeafGrammar | LeafListGrammar | ChoiceGrammar, min=0),
               CLOSEBRACE
               )


class ListKeyword(Grammar):
    grammar = (L("list"))


class ListGrammar(Grammar):
    grammar = (ListKeyword, Name,
               OPENBRACE,
               REPEAT(Key | Unique | Description | IfFeature | OrderedBy | REF("Uses") | MinElements | MaxElements | ReferenceGrammar | REF("ContainerGrammar") | REF("ListGrammar") | LeafGrammar | LeafListGrammar | ChoiceGrammar | Config, min=0),
               CLOSEBRACE
               )


class Uses(Grammar):
    grammar = (L('uses'), WORD('"a-zA-Z0-9', restchars='a-zA-Z0-9:\.\-"', fullmatch=True, escapes=True),
               OR(
        (OPENBRACE,
                REPEAT(Description | Refine | IfFeature | Status | ReferenceGrammar, min=0),
                CLOSEBRACE
             ),
        L(';')
    )
    )


class NotificationKeyword(Grammar):
    grammar = (L('notification'))


class Notification(Grammar):
    grammar = (NotificationKeyword, Name,
               OR(L(';'),

            (
                OPENBRACE,
                REPEAT(ChoiceGrammar | ContainerGrammar | Description | Grouping | IfFeature | LeafGrammar |
                       LeafListGrammar | ListGrammar | ReferenceGrammar | Status | TypedefGrammar | Uses, min=0),
                CLOSEBRACE
        )
        )
    )


class AugmentKeyword(Grammar):
    grammar = (L('augment'))


class AugmentName(Grammar):
    grammar = (WORD('a-zA-Z/"', restchars='a-zA-Z:/0-9\\!=\'\s\t\-"',
                    fullmatch=True, escapes=True))


class Augment(Grammar):
    grammar = (AugmentKeyword, AugmentName,
               OPENBRACE,
               REPEAT(When | IfFeature | Description | ReferenceGrammar |
                      LeafGrammar | ContainerGrammar | CaseGrammar, min=1),
               CLOSEBRACE
               )
