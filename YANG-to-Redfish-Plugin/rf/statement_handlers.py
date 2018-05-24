# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

from xml.etree.ElementTree import Element, SubElement
import rf.xml_convenience as xml_convenience
import rf.redfishtypes as redfishtypes
from rf.redfishtypes import get_valid_csdl_identifier
import rf.csdltree


# This file contains a series of handle_XXXXX functions.
# Each function handles a keyword and any internal grammar such
# as the case of type metadata.

def handle_generic(yang_keyword, yang_arg, yang_children = [], target = None, target_entity = None, target_parent = None, list_of_xml=None, imports=None, types=None, prefix=None):
    #
    if yang_keyword == 'description':
        if yang_arg[-1] != '.':
            yang_arg.append('.')
    annotation = xml_convenience.add_annotation(
            target, {'Term': redfishtypes.get_descriptive_properties_mapping(yang_keyword),
                     'String':  yang_arg
                     }
            )
    
    handle_generic_children(yang_children, annotation, target_entity, target_parent, list_of_xml, imports, types, prefix)

    return annotation

def handle_generic_children(yang_children, target, target_entity=None, target_parent=None, list_of_xml=None, imports=None, types=None, prefix=None):
    for child in yang_children:
        rf.csdltree.build_tree_repeat(child, target, target_entity=target_entity, target_parent=target_parent, list_of_xml=list_of_xml, topleveltypes=types, toplevelimports=imports, prefix=prefix) 

def handle_generic_node(yang_keyword, yang_arg, yang_children):
    annotation = xml_convenience.add_annotation(
            None, {'Term': redfishtypes.get_descriptive_properties_mapping(yang_keyword),
                    'EnumMember':  'RedfishYang.Mandatory/' + value
                     })
    return annotation

def handle_generic_modifier(yang_keyword, yang_arg, target):
    convert_to_csdl = {
            "namespace": "yangns",
            "prefix": "Alias"
            }

    yang_keyword = convert_to_csdl.get(yang_keyword, yang_keyword.capitalize)

    return
    target.set(yang_keyword, get_valid_csdl_identifier(yang_arg))

def handle_choice(yang_keyword, yang_arg, yang_children, target, target_entity, target_parent, list_of_xml, imports, types, prefix):
    new_xml = []
    annotation = handle_generic(yang_keyword, yang_arg, yang_children, target)
    for case in yang_children:
        handle_generic_children(case.substmts, target, target_entity=target_entity, target_parent=target_parent, list_of_xml=list_of_xml, imports=imports, types=types, prefix=prefix)
    return annotation 


def handle_enum(yang_keyword, yang_arg, yang_children, target):
    member_node = SubElement(target, 'Member')
    member_node.set('Name', yang_arg)

    annotation = xml_convenience.add_annotation(
            target, {'Term': redfishtypes.get_descriptive_properties_mapping(yang_keyword),
                     'String':  yang_arg
                     }
            )

    handle_generic_children(yang_children, member_node)

    return member_node


def handle_rpc(yang_keyword, yang_arg, yang_children, schema_xml, module_xml):
    annotation = handle_generic(yang_keyword, yang_arg, yang_children, schema_xml)
    ds_node = module_xml.find('./')
    schema_node = ds_node.findall('./')[0]

    inp, desc = None, None
    for item in yang_children:
        if type_repeat == 'input':
            inp = item
        if type_repeat == 'description':
            desc = item


    
# Handle the typedef statement
def handle_typedef(yang_keyword, yang_arg, yang_children, schema_xml, module_xml, no_append=False):
    """
    Handle typedef statement.
    :param items: Grammar items.
    :param xml_parent: Node to which sub elements are to be added.
    """
    type_tag, desc, ref_tag = None, None, None

    for item in yang_children:
        type_repeat = item.keyword
        if type_repeat == 'type':
            type_tag = item
        if type_repeat == 'description':
            desc = item
        if type_repeat == 'reference':
            ref_tag = item


    annotation = xml_convenience.add_annotation(
            None, {'Term': redfishtypes.get_descriptive_properties_mapping(type_tag.keyword),
                     'String':  type_tag.arg
                     }
            )

    if type_tag is None:
        print("This type tag shouldn't be missing")
        return

    if type_tag.arg == 'enumeration':
        new_node = Element('EnumType')
        new_node.set('Name', get_valid_csdl_identifier(str(yang_arg)))

        handle_generic_children(type_tag.substmts, new_node)
        
        handle_generic_children([x for x in yang_children if x.keyword != 'type'], new_node)


    else: 
        new_node = Element('TypeDefinition')
        new_node.set('Name', get_valid_csdl_identifier(str(yang_arg)))

        handle_generic_children(type_tag.substmts, new_node)
        
        handle_generic_children([x for x in yang_children if x.keyword != 'type'], new_node)

        var_type = type_tag.arg.replace('"', '')

        new_node.set('UnderlyingType', redfishtypes.types_mapping.get(var_type, var_type))

    if not no_append:
        schema_xml.append(new_node) 
    return get_valid_csdl_identifier(str(yang_arg)), new_node


def handle_type(type_tag, xml_node, parent_node, parent_entity, imports, types):
    """
    Handle 'type' statement 
    :param type_grammar_items: Grammar items within type definition in 
    YANG model
    :param xml_node: XML node to which sub elements are to be added.
    """
    # What are we?  Simple Type?  Get our info.
    var_type = get_valid_csdl_identifier(type_tag.arg)
    
    annotation = xml_convenience.add_annotation(
            xml_node, {'Term': 'RedfishYang.YangType',
                     'String':  "Unknown"
                     }
            )

     

    # If there's an import, let's consider it ':' = '.'
    # If it's in the imports, then add the import
    # If it is a simple name already in types available, then put it in file
    if var_type != 'enumeration': 
        xml_top = rf.csdltree.current_xml_top[-1]
        if '.' in var_type:
            # This is an import from another file, add to CSDL imports
            importname = get_valid_csdl_identifier(var_type.split('.')[0])
            if importname in imports:
                xml_convenience.add_import(xml_top, imports[importname], importname if importname != imports[importname] else None)
            var_type = redfishtypes.types_mapping.get(var_type, var_type)

        elif var_type in types:
            # If we haven't defined this type, this must be added to imports
            ds_node = xml_top.find('./')
            schema_node = ds_node.findall('./')[1]
            namespace = schema_node.attrib.get('Namespace')
            available_types = list()

            for ref in schema_node:
                if str(ref.tag) not in ['TypeDefinition', 'EnumType']:
                    continue
                available_types.append(ref.attrib.get('Name'))

            if get_valid_csdl_identifier(var_type) not in available_types:
                schema_node.append(types[var_type])

            if namespace is None:
                print("Namespace shouldn't be none {}".format(parent_entity.attrib))
                get_valid_csdl_identifier(redfishtypes.types_mapping.get(var_type, var_type))

            elif namespace is not "":
                namespace = namespace + "."
            var_type = namespace + var_type
        
        else:
            # If it is neither, it must be primitive
            primitive_type = var_type
            csdl_type = redfishtypes.types_mapping.get(
                primitive_type, 'Yang.' + primitive_type)
            yang_type = primitive_type
            var_type = redfishtypes.types_mapping.get(var_type, var_type)
            """
            if (xml_node is not None) and (xml_node.get_type() == 'LeafListKeyword'):
                xml_node.set('Type', 'Collection(' + csdl_type + ')')
            else:  # Tree_node is None : RPC Leaf; Or type is Leaf
                xml_node.set('Type', csdl_type)
            if type_grammar == 'SimpleTypeWithMetadata':
                metadata_grammar = type_grammar_items[1].elements[2]
                metadata_grammar_type = str(type(metadata_grammar))
                handle_metadata_grammar(metadata_grammar, xml_node)
            """
        new_type = var_type
        if 'Collection(' in xml_node.get('Type',''):
            new_type = 'Collection({})'.format(var_type)
        xml_node.set('Type', get_valid_csdl_identifier(var_type))
    else:
        yang_item = type_tag.parent
        yang_keyword = yang_item.keyword
        yang_arg = yang_item.arg.replace('\n',' ') if yang_item.arg is not None else '-'

        if hasattr(yang_item, 'i_children'):
            yang_children = yang_item.i_children if len(yang_item.i_children) > 0 else []
        yang_children = yang_item.substmts
        td, nmd = handle_typedef(yang_keyword, yang_arg, yang_children, parent_node, parent_entity, no_append=True)
        type_tag.arg = td
        handle_type(type_tag, xml_node, parent_node, parent_entity, {}, {td: nmd})

    annotation.set('String', var_type)

    return
