# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from xml.etree.ElementTree import Element, SubElement
import rf.xml_convenience as xml_convenience
import rf.redfishtypes as redfishtypes
import rf.csdltree

def get_valid_csdl_identifier(name):
    """
    Replace characters that are invalid in CSDL with appropriate valid ones
    """
    return name.replace('-', '_').replace(':', '.')

# This file contains a series of handle_XXXXX functions.
# Each function handles a keyword and any internal grammar such
# as the case of type metadata.

def handle_generic(yang_keyword, yang_arg, yang_children = [], target = None, target_entity = None, target_parent = None, list_of_xml=None, imports=None, types=None):
    #
    annotation = xml_convenience.add_annotation(
            target, {'Term': redfishtypes.get_descriptive_properties_mapping(yang_keyword),
                     'String':  yang_arg
                     }
            )
    
    handle_generic_children(yang_children, annotation, target_entity, target_parent, list_of_xml, imports, types)

    return annotation

def handle_generic_children(yang_children, target, target_entity=None, target_parent=None, list_of_xml=None, imports=None, types=None):
    for child in yang_children:
        rf.csdltree.build_tree_repeat(child, target, target_entity=target_entity, target_parent=target_parent, list_of_xml=list_of_xml, topleveltypes=types, toplevelimports=imports) 

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

    target.set(yang_keyword, get_valid_csdl_identifier(yang_arg))

def handle_choice(yang_keyword, yang_arg, yang_children, target, target_entity, target_parent, list_of_xml, imports, types):
    new_xml = []
    annotation = handle_generic(yang_keyword, yang_arg, yang_children, target)
    for case in yang_children:
        handle_generic_children(case.substmts, target, target_entity=target_entity, target_parent=target_parent, list_of_xml=list_of_xml, imports=imports, types=types)
    return annotation 




def handle_enum(yang_keyword, yang_arg, yang_children, target):
    member_node = SubElement(target, 'Member')
    member_node.set('Name', yang_arg)

    handle_generic_children(yang_children, member_node)

    return member_node


# Handle the typedef statement
def handle_typedef(yang_keyword, yang_arg, yang_children, schema_xml, module_xml):
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
    var_type = get_valid_csdl_identifier(type_tag.arg.replace('"', ''))
    annotation = SubElement(xml_node, 'Annotation')
    annotation.set('Term', redfishtypes.get_descriptive_properties_mapping('YangType'))

    # If there's an import, let's consider it ':' = '.'
    # If it's in the imports, then add the import
    # If it is a simple name already in types available, then put it in file
    if var_type != 'enumeration': 
        if '.' in var_type:
            # This is an import from another file, add to CSDL imports
            importname = var_type.split(':')[0]
            if importname in imports:
                xml_convenience.add_import(parent_node, imports[importname], importname if importname != imports[importname] else None)
            xml_node.set('Type', get_valid_csdl_identifier(redfishtypes.types_mapping.get(var_type, var_type)))

        elif var_type in types:
            # If we haven't defined this type, this must be added to imports
            ds_node = parent_node.find('./')
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
                input(get_valid_csdl_identifier(redfishtypes.types_mapping.get(var_type, var_type)))

            elif namespace is not "":
                namespace = namespace + "."
            xml_node.set('BaseType', str(namespace) + get_valid_csdl_identifier(redfishtypes.types_mapping.get(var_type, var_type)))
        
        else:
            # If it is neither, it must be primitive
            primitive_type = var_type
            csdl_type = redfishtypes.types_mapping.get(
                primitive_type, 'Yang.' + primitive_type)
            yang_type = primitive_type
            xml_node.set('Type', get_valid_csdl_identifier(redfishtypes.types_mapping.get(var_type, var_type)))
            return
            if (xml_node is not None) and (xml_node.get_type() == 'LeafListKeyword'):
                xml_node.set('Type', 'Collection(' + csdl_type + ')')
            else:  # Tree_node is None : RPC Leaf; Or type is Leaf
                xml_node.set('Type', csdl_type)
            if type_grammar == 'SimpleTypeWithMetadata':
                metadata_grammar = type_grammar_items[1].elements[2]
                metadata_grammar_type = str(type(metadata_grammar))
                handle_metadata_grammar(metadata_grammar, xml_node)

    annotation.set('String', var_type)

    return
    # Set some annotation properties because we can do it now. Other
    # option is to repeat the annotation statements in the if and else sections
    if None:
        # if the Type of this variable is an enumeration, then
        xml_node.set('Type', 'Edm:Enumeration')
        enumeration_items = type_grammar_items[1].elements[2].elements
        yang_type = 'enumeration'

        name = tree_node.get_name()
        enumeration_node = SubElement(xml_node, 'EnumType')
        enumeration_node.set('Name', name + "Enumeration")

        for enumeration_item in enumeration_items:
            enum_item_name = None
            enum_item_value = None
            enum_item_type = str(type(enumeration_item))
            enum_member = SubElement(enumeration_node, 'Member')
            if enum_item_type == 'EnumItemTypeA':
                enum_item_name = enumeration_item.elements[1].string.strip('"')
                enum_item_value = enumeration_item.elements[
                    3].elements[0].elements[1].string.strip('"')
                enum_member.set('Name', enum_item_name)
                enum_member.set('Value', enum_item_value)
            else:
                enum_item_name = enumeration_item.elements[1].string.strip('"')
                enum_member.set('Name', enum_item_name)
            xml_convenience.add_annotation(enum_member, {'Term': 'RedfishYang.enum', 'String': enum_item_name})

# Seperate from the old stuff

pass
pass
pass
pass

def handle_grouping(group_elements, tree_node, xml_node, list_of_xml, target_dir, logger):
    logger.warning(
        'Found grouping statement. Please run a pre-processor to handle it. Ignoring grouping keyword')
    for item in group_elements:
        itemtype = str(type(item))
        logger.debug('Found within group: ' + itemtype)
        if itemtype == 'GroupingKeyword':
            continue
        elif item == 'Name':
            logger.debug('Found group : ' + item.elements[0].string.strip('"'))
        elif itemtype == 'Description':
            continue
        elif itemtype == '<REPEAT>':
            repeat_items = item.elements
            for repeat_item in repeat_items:
                repeat_item_type = str(type(repeat_item))
                logger.debug(
                    'Found repeat item within group: ' + repeat_item_type)
                if repeat_item_type == 'ContainerGrammar' or repeat_item_type == 'LeafGrammar':
                    (child_node, xml_child) = build_tree(tree_node, xml_node,
                                                         repeat_item.elements, list_of_xml, target_dir, logger)
                    tree_node.add_child(child_node)
                    if repeat_item_type == 'LeafGrammar':
                        xml_node.append(xml_child)
                elif repeat_item_type == 'ReferenceGrammar':
                    handle_reference(repeat_item, xml_node)

def tr(input_string):
    """ Return the input string after trimming within & outside the string."""
    return(' '.join(input_string.split()))


def handle_name(name_tag, target):
    """ Given a parsed Name tag, apply it to target node """
    csdl_name = get_valid_csdl_identifier(name_tag.arg)
    return csdl_name


def handle_rpc(rpc_tag, xml_node):
    """
    Handle RPC statement.
    """
    rpc_items = rpc_tag.elements
    for item in rpc_items:
        print("\t",item.keyword)
        print("\t","\t", item.arg)
        item_type = str(type(item))
        if item_type == 'RpcKeyword':
            action_node = SubElement(xml_node, 'Action')
            xml_convenience.add_annotation(action_node, {'Term': 'RedfishYang.NodeType', 'String': redfishtypes.get_node_types_mapping(item_type)})
        elif item_type == 'Name':
            name = item.elements[0].string.strip('"')
            csdl_name = get_valid_csdl_identifier(name)
            action_node.set('Name', csdl_name)
        elif item_type == 'Description':
            description = (tr(item.elements[1].string)).strip('"')
            xml_convenience.add_annotation(xml_node, {'Term': redfishtypes.get_descriptive_properties_mapping('description'), 'String': description})
        elif item_type == '<REPEAT>':
            repeat_items = item.elements
            for repeat_item in repeat_items.elements:
                # repeat_item_type = str(type(repeat_item))
                if item_type == 'InputGrammar':
                    handle_print(repeat_item.elements, action_node, xml_node)
                elif item_type == 'OutputGrammar':
                    handle_output(repeat_item.elements, action_node, xml_node)
        elif item_type == 'InputGrammar':
            handle_print(item.elements, action_node, xml_node)
        elif item_type == 'OutputGrammar':
            handle_output(item.elements, action_node, xml_node)
        elif item_type == 'Unmapped':
            handle_unmapped(item.elements, action_node)
        elif item_type == 'CLOSEBRACE':
            continue
        else:
            continue


def handle_print(input_grammar, action_node, xml_node):
    """ 
    Handle input statment
    """
    name = action_node.get('Name')
    param = SubElement(action_node, 'Parameter')
    param.set('Name', name + 'Input')
    param.set('Type', name + 'InputType')
    param_annotation = xml_convenience.add_annotation(param, {'Term': 'RedfishYang.NodeType',
                                              'EnumMember': 'RedfishYang.NodeTypes/input'})
    for item in input_grammar:
        print("\t",item.keyword)
        print("\t","\t", item.arg)
        item_type = str(type(item))
        if item_type == 'InputKeyword':
            continue
        elif item_type == 'LeafGrammar':
            handle_rpc_leaf(item, name + 'InputType', xml_node)
        else:
            continue


def handle_output(output_grammar, action_node, xml_node):
    """
    Handle output statment
    """
    name = action_node.get('Name')
    return_type = SubElement(action_node, 'Parameter')
    return_type.set('Name', name + 'Output')
    return_type.set('Type', name + 'OutputType')
    return_type_annotation = xml_convenience.add_annotation(return_type, {
        'Term': 'RedfishYang.NodeType',
        'String': 'RedfishYang.NodeTypes/output'
    }
    )
    for item in output_grammar:
        print("\t",item.keyword)
        print("\t","\t", item.arg)
        item_type = str(type(item))
        if item_type == 'OutputKeyword':
            continue
        elif item_type == 'LeafGrammar':
            handle_rpc_leaf(item, name + 'OutputType', xml_node)
        else:
            continue


def handle_rpc_leaf(leaf_item, name, xml_node):
    """
    Handle leaf elements within RPC.
    """
    leaf_item_grammar = leaf_item.elements
    complex_type = SubElement(xml_node, 'ComplexType')
    complex_type.set('Name', name)
    property_node = SubElement(complex_type, 'Property')
    for item in leaf_item_grammar:
        item_type = str(type(item))
        if item_type == 'Name':
            property_node.set('Name', item.string.strip('"'))
        elif item_type == '<REPEAT>':
            for repeat_item in item.elements:
                repeat_item_type = str(type(repeat_item))
                if repeat_item_type == 'Type':
                    handle_type(repeat_item, None, xml_node)


def handle_mandatory(mandatory_tag, xml_node):
    """
    Handle 'mandatory' statment
    """
    items = mandatory_tag.elements
    value = items[1].string.strip('"')
    annotation_mandatory = xml_convenience.add_annotation(xml_node, {'Term': 'RedfishYang.mandatory',
                                                     'EnumMember':  'RedfishYang.Mandatory/' + value
                                                     }
                                          )


def handle_config(config_tag, xml_node):
    """
    Handle config statement.
    """
    items = config_tag.elements
    value = items[1].string.strip('"')
    annotation_config = xml_convenience.add_annotation(xml_node, {'Term': 'RedfishYang.config',
                                                  'EnumMember':  'RedfishYang.ConfigPermission/' + value
                                                  }
                                       )
    return value


def handle_default(default_tag, xml_node):
    """
    Handle 'default'
    """
    items = default_tag.elements
    xml_node.set('DefaultValue', items[1].string.strip('"'))



def handle_key(key_tag, xml_node):
    """
    Handle 'key'
    """
    key_items = key_tag.elements
    key_node = None
    key_node = xml_node.find('Key')
    if key_node is None:
        key_node = SubElement(xml_node, 'Key')
    for keyname in key_items[1].string.strip('"').split(' '):
        prop_ref = SubElement(key_node, 'PropertyRef')
        prop_ref.set('Name', keyname) 



def handle_unmapped(unmapped_tag, xml_node):
    """
    Handle unmapped
    """
    unmapped_items = unmapped_tag.elements
    xml_convenience.add_annotation(xml_node, {
        'Term': redfishtypes.get_descriptive_properties_mapping('Statement'),
        'String': unmapped_items[0].string.strip('"')
    }
    )

def handle_status(status_tag, xml_node):
    """
    Handle 'status'
    """
    status_items = status_tag.elements
    xml_convenience.add_annotation(xml_node, {
        'Term': redfishtypes.get_descriptive_properties_mapping('status'),
        'EnumMember': 'RedfishYang.NodeStatus/' + status_items[1].string.strip('"')
    }
    )


def handle_yin(yin_tag, xml_node):
    """
    Handle 'yin'
    """
    yin_elements = yin_tag.elements
    value = yin_elements[1].string.strip('"')
    xml_convenience.add_annotation(xml_node, {
        'Term': redfishtypes.get_descriptive_properties_mapping('YinElement'),
        'EnumMember': 'RedfishYang.YinElement/' + value
    })


def handle_anyxml(anyxml, xml_node, anyxml_counter):
    """
    Handle 'anyxml'.
    """
    term_node = SubElement(xml_node, 'Term')
    term_node.set('Name', 'IsXml')
    term_node.set('Type', 'Edm.Boolean')
    term_node.set('Default', 'True')
    xml_convenience.add_annotation(term_node,
                   {
                       'Term': redfishtypes.get_descriptive_properties_mapping('Description'),
                       'String': 'The string type contains XML'
                   }
                   )

    typedef_node = SubElement(xml_node, 'TypeDefinition')
    typedef_node.set('Name', 'XmlBlock')
    typedef_node.set('UnderlyingType', 'Edm.String')
    xml_convenience.add_annotation(
        typedef_node, {'Term': redfishtypes.get_descriptive_properties_mapping('isxml')})

    property_node = SubElement(xml_node, 'Property')
    property_node.set('Name', 'Anyxml_' + str(anyxml_counter))
    property_node.set('Type', redfishtypes.get_descriptive_properties_mapping('xmlblock'))
    xml_convenience.add_annotation(property_node, {
                   'Term': 'RedfishYang.AnyxmlText', 'String': anyxml.arg})

    #anyxml_data = anyxml_items[1].string.strip('"')
    #anyxml_root = fromstring(anyxml_data)
    # property_node.append(anyxml_root)


def handle_extension(extension_tag, xml_node):
    """
    Handle 'extension'
    """
    extension_items = extension_tag.elements
    for item in extension_items:
        item_type = str(type(item))
        if item_type == 'Name':
            extension_annotation = xml_convenience.add_annotation(xml_node, {
                'Term': redfishtypes.get_descriptive_properties_mapping('extension'),
                'String': extension_items[1].string.strip('"')
            }
            )
        elif item_type == '<REPEAT>':
            repeat_items = item.elements
            for repeat_item in repeat_items:
                repeat_item_type = str(type(repeat_item))
                if repeat_item_type == 'Description':
                    description_text = (tr(repeat_item[1].string)).strip('"')
                    xml_convenience.add_annotation(extension_annotation,
                                   {
                                       'Term': redfishtypes.get_descriptive_properties_mapping('description'),
                                       'String': description_text
                                   }
                                   )
                elif repeat_item_type == 'Argument':
                    xml_convenience.add_annotation(extension_annotation,
                                   {
                                       'Term': redfishtypes.get_descriptive_properties_mapping('argument'),
                                       'String': repeat_item.elements[1].string.strip('"')
                                   }
                                   )

        else:
            continue
