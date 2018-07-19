# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

from xml.etree.ElementTree import Element, SubElement
import rf.xml_convenience as xml_convenience
import rf.redfishtypes as redfishtypes
from rf.redfishtypes import get_valid_csdl_identifier
import rf.csdltree


# annotation cleanup
def collectAnnotations(node):
    allAnnotations = node.findall('Annotation')

    collected = {}
    for a in allAnnotations:
        term = a.attrib.get('Term')
        if term not in collected:
            collected[term] = []
        collected[term].append(a)

    for key in collected:
        target = collected[key]
        if len(target) > 1:
            Collection = SubElement(node, 'Collection')
            for a in target:
                Record = SubElement(Collection, 'Record')
                Record.append(a)
                node.remove(a)

def collectChildren(yang_item):
    yang_keyword = yang_item.keyword
    if hasattr(yang_item, 'i_children'):
        content = yang_item.i_children if len(yang_item.i_children) > 0 else []
        #print(yang_keyword, [tag.keyword for tag in content if tag not in yang_item.substmts])
        content = yang_item.substmts + [tag for tag in content if tag not in yang_item.substmts]
    else:
        #print(yang_keyword, 'HAS NO ICHILD')
        content = yang_item.substmts
    return content

# This file contains a series of handle_XXXXX functions.
# Each function handles a keyword and any internal grammar such
# as the case of type metadata.

def handle_generic(yang_keyword, yang_arg, yang_children=[], target=None, target_entity=None, target_parent=None, list_of_xml=None, imports=None, types=None, prefix=None, generic=False, keyword_raw=None):
    #
    yang_raw_keyword = keyword_raw if keyword_raw else yang_keyword

    if type(yang_keyword) == tuple:
        print("We don't recognize keyword, create as statement")
        annotation = handle_generic_statement(yang_raw_keyword, yang_arg, target)

    elif yang_keyword == 'description' and not generic:
        if yang_arg[-1] != '.':
            yang_arg = yang_arg + '.'
        annotation = xml_convenience.add_annotation(
            target, {'Term': 'OData.Description', 'String': yang_arg})

    else:
        annotation = xml_convenience.add_annotation(
            target, {'Term': redfishtypes.get_descriptive_properties_mapping(yang_keyword), 'String': yang_arg})

    if generic:
        for yang_item in yang_children:
            child_yang_keyword = yang_item.keyword
            child_yang_raw_keyword = yang_item.raw_keyword
            child_yang_arg = yang_item.arg.replace('\n',' ') if yang_item.arg is not None else ''
            child_yang_children = collectChildren(yang_item) 
            handle_generic(child_yang_keyword, child_yang_arg, child_yang_children, annotation, generic=True, keyword_raw=child_yang_raw_keyword, prefix=prefix) 
        collectAnnotations(annotation)
    else:
        handle_generic_children(yang_children, annotation, target_entity, target_parent, list_of_xml, imports, types, prefix)

    return annotation



def handle_generic_statement(yang_keyword, yang_arg, target):
    if type(yang_keyword) is tuple:
        yang_keyword = ':'.join(yang_keyword)

    string = yang_keyword
    string += ' ' + yang_arg if yang_arg not in ['', ' ', None] else ''
    annotation = xml_convenience.add_annotation(
        target, {'Term': 'RedfishYang.statement', 'String': yang_keyword})
    return annotation


def handle_generic_children(yang_children, target, target_entity=None, target_parent=None, list_of_xml=None, imports=None, types=None, prefix=None):
    for child in yang_children:
        rf.csdltree.build_tree_repeat(child, target, target_entity=target_entity, target_parent=target_parent, list_of_xml=list_of_xml, topleveltypes=types, toplevelimports=imports, prefix=prefix) 
    collectAnnotations(target)


def handle_generic_node(yang_keyword, yang_arg, target):
    term, enummember = redfishtypes.get_annotation_enum(yang_keyword, yang_arg)
    annotation = xml_convenience.add_annotation(target, {'Term': term, 'EnumMember': enummember})
    return annotation


def handle_generic_modifier(yang_keyword, yang_arg, target):
    convert_to_csdl = {
            "namespace": "xmlns",
            "prefix": "Alias",
            "default": "DefaultValue"

            }

    handle_generic(yang_keyword, yang_arg, [], target)
    if yang_keyword not in ["namespace"]:
        yang_keyword = convert_to_csdl.get(yang_keyword, yang_keyword.capitalize())
        target.set(yang_keyword, get_valid_csdl_identifier(yang_arg))


"""
   As a shorthand, the "case" statement can be omitted if the branch
   contains a single "anyxml", "container", "leaf", "list", or
   "leaf-list" statement.  In this case, the identifier of the case node
   is the same as the identifier in the branch statement.  The following
   example:
"""
def handle_choice(yang_keyword, yang_arg, yang_children, target, target_entity, target_parent, list_of_xml, imports, types, prefix):
    yang_children = [tag for tag in yang_children if tag.keyword not in ['anyxml',  'container', 'leaf', 'list', 'leaf-list']]
    annotation = handle_generic(yang_keyword, yang_arg, yang_children, target, target_entity, prefix=prefix)
    for case in yang_children: 
        case_children = collectChildren(case)
        handle_generic_children(case_children, target, target_entity=target_entity, target_parent=target_parent, list_of_xml=list_of_xml, imports=imports, types=types, prefix=prefix)
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
    namespace = schema_node.attrib.get('Namespace')

    action = Element('Action')
    action.set('Name', yang_arg)
    action.set('IsBound', 'true')

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
    inner_annotation = xml_convenience.add_annotation(
            None, {'Term': 'RedfishYang.YangType',
                     'String':  "Unknown"
                     }
            )

    if type_tag is None:
        print("This type tag shouldn't be missing")
        return None, None

    if type_tag.arg == 'enumeration':
        new_node = Element('EnumType')
        new_node.set('Name', get_valid_csdl_identifier(str(yang_arg)))

        handle_generic_children(collectChildren(type_tag), new_node)
        
        handle_generic_children([x for x in yang_children if x.keyword != 'type'], new_node)


    else: 
        new_node = Element('TypeDefinition')
        new_node.set('Name', get_valid_csdl_identifier(str(yang_arg)))

        yang_type = 'empty'
        for item in [x for x in yang_children if x.keyword == 'type']:
            yang_type = item.arg
            yang_children_inner = collectChildren(item)
            if item.arg == 'union':
                union_annotation = xml_convenience.add_annotation(
                        new_node, {'Term': 'RedfishYang.union'})
                col = SubElement(union_annotation, 'Collection') 
                for child in yang_children_inner:
                    if child.keyword != 'type':
                        continue
                    else:
                        inn = SubElement(col, 'String')
                        inn.text = '"{}"'.format(redfishtypes.get_valid_csdl_identifier(child.arg))

            handle_generic_children([x for x in yang_children_inner if x.keyword != 'type'], inner_annotation)
        
        handle_generic_children([x for x in yang_children if x.keyword != 'type'], new_node)

        var_type = type_tag.arg.replace('"', '')

        # default to primitive instead of string, UnderlyingType must be dereferenced
        new_node.set('UnderlyingType', redfishtypes.types_mapping.get(var_type, 'Edm.Primitive'))
        inner_annotation.set('String', yang_type)
        new_node.append(inner_annotation) 

    if not no_append:
        schema_xml.append(new_node) 
    return yang_arg, new_node


def handle_type(type_tag, xml_node, parent_node, parent_entity, imports, types):
    """
    Handle 'type' statement 
    :param type_grammar_items: Grammar items within type definition in 
    YANG model
    :param xml_node: XML node to which sub elements are to be added.
    """
    # What are we?  Simple Type?  Get our info.
    var_type = get_valid_csdl_identifier(type_tag.arg)
    var_type = type_tag.arg
    yang_type = var_type
    
    annotation = xml_convenience.add_annotation(
            None, {'Term': 'RedfishYang.YangType',
                     'String':  "Unknown"
                     }
            )

    # If there's an import, let's consider it ':' = '.'
    # If it's in the imports, then add the import
    # If it is a simple name already in types available, then put it in file
    if var_type != 'enumeration': 
        xml_top = rf.csdltree.current_xml_top[-1]
        if ':' in var_type:
            # This is an import from another file, add to CSDL imports
            importname = var_type.split(':')[0]
            if importname in imports:
                ns = imports[importname] + '.v1_0_0' 
                xml_convenience.add_import(xml_top, imports[importname], importname if importname != imports[importname] else None, ns)
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
            yang_type = primitive_type
            var_type = redfishtypes.types_mapping.get(var_type, 'RedfishYang.' + var_type)
            yang_children = collectChildren(type_tag)
            if primitive_type == 'union':
                union_annotation = xml_convenience.add_annotation(
                        xml_node, {'Term': 'RedfishYang.union'})
                col = SubElement(union_annotation, 'Collection') 
                for child in yang_children:
                    if child.keyword != 'type':
                        continue
                    else:
                        inn = SubElement(col, 'String')
                        inn.text = '"{}"'.format(redfishtypes.get_valid_csdl_identifier(child.arg))
            handle_generic_children([x for x in yang_children if x.keyword != 'type'], annotation)

                
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
        xml_node.set('Type', get_valid_csdl_identifier(new_type))
    else:
        yang_item = type_tag.parent
        yang_keyword = yang_item.keyword
        yang_arg = yang_item.arg.replace('\n',' ') if yang_item.arg is not None else '-'
        yang_children = collectChildren(yang_item)

        td, nmd = handle_typedef(yang_keyword, yang_arg, yang_children, parent_node, parent_entity, no_append=True)
        type_tag.arg = td
        new_annotation = handle_type(type_tag, xml_node, parent_node, parent_entity, {}, {td: nmd})
        xml_node.remove(new_annotation)

    annotation.set('String', yang_type)
    xml_node.append(annotation) 

    return annotation
