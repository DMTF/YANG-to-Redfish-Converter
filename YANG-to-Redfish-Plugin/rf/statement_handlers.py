# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from xml.etree.ElementTree import Element, SubElement
import rf.xml_convenience as xml_convenience
import rf.redfishtypes as redfishtypes

# This file contains a series of handle_XXXXX functions.
# Each function handles a keyword and any internal grammar such
# as the case of type metadata.


def get_valid_csdl_identifier(name):
    """
    Replace characters that are invalid in CSDL with appropriate valid ones
    """
    return name.replace('-', '_').replace(':', '.')


def handle_case_grammar(case_grammar_elements, tree_node, choice_annotation_node, xml_annotation_parent, list_of_xml, target_dir, logger):
    for item in case_grammar_elements:
        item_type = (str(type(item)))
        if item_type == 'CaseKeyword':
            continue
        elif item_type == 'Name':
            casename = item.elements[0].string.strip('"')
            case_csdl_name = get_valid_csdl_identifier(casename)
            case_annotation = xml_convenience.add_annotation(choice_annotation_node, {
                'Term': redfishtypes.get_descriptive_properties_mapping('Case'),
                'String': case_csdl_name
            })
            logger.debug('Handling case: ' + casename)
        elif item_type == '<REPEAT>':
            repeat_items = item.elements
            for repeat_item in item.elements:
                repeat_item_type = str(type(repeat_item))
                if repeat_item_type == 'ContainerGrammar':
                    (child_node, xml_child_node) = build_tree(
                        tree_node, xml_annotation_parent, repeat_item.elements, list_of_xml, target_dir, logger)
                    tree_node.add_child(child_node)
                elif (repeat_item_type == 'LeafGrammar'):
                    (child_node, xml_child_node) = build_tree(
                        tree_node, xml_annotation_parent, repeat_item.elements, list_of_xml, target_dir, logger)
                    xml_annotation_parent.append(xml_child_node)
                    tree_node.add_child(child_node)
                    name = child_node.get_name()
                    nodename_annotation = xml_convenience.add_annotation(case_annotation,
                                                         {
                                                             'Term': 'RedfishYang.NodeName',
                                                             'String': name
                                                         }
                                                         )
                    nodetype_annotation = xml_convenience.add_annotation(nodename_annotation,
                                                         {
                                                             'Term': 'RedfishYang.NodeType',
                                                             'EnumMember': get_node_types_mapping('LeafKeyword')
                                                         }
                                                         )
                    for xml_child in xml_annotation_parent.findall('Property'):
                        child_name = xml_child.get('Name')
                        if child_name == name:
                            property_case_annotation = xml_convenience.add_annotation(xml_child,
                                                                      {'Term': redfishtypes.get_descriptive_properties_mapping('case'), 'String': child_name}
                                                                      )
                            property_choice_annotation = xml_convenience.add_annotation(xml_child,
                                                                        {'Term': redfishtypes.get_descriptive_properties_mapping('choice'), 'String' : choice_annotation_node.get('String') }
                                                                        )


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

def handle_choice_grammar(items, tree_node, xml_node, xml_parent, list_of_xml, target_dir, logger):
    annotation_node = None
    for item in items:
        item_type = str(type(item))
        if item_type == 'ChoiceKeyword' or item_type == 'OPENBRACE':
            continue
        elif item_type == 'Name':
            name = item.elements[0].string.strip('"')
            csdl_name = get_valid_csdl_identifier(name)
            logger.debug('Handling choice: ' + name)
            yang_choice_annotation =  xml_convenience.add_annotation(xml_node, {
                'Term': redfishtypes.get_descriptive_properties_mapping('Choice'),
                'String': csdl_name
            }
            )
        elif item_type == 'Description':
            description = (tr(item.elements[1].string)).strip('"')
            yang_description_annotation = xml_convenience.add_annotation(yang_choice_annotation, {
                'Term': redfishtypes.get_descriptive_properties_mapping('description'),
                'String': description
            }
            )
        elif item_type == '<REPEAT>':  # case will start here
            repeat_item_elements = item.elements
            for repeat_item in repeat_item_elements:
                repeat_item_type = str(type(repeat_item))
                if repeat_item_type == 'CaseGrammar':
                    handle_case_grammar(repeat_item, tree_node,
                                        yang_choice_annotation, xml_node, list_of_xml, target_dir, logger)
                elif repeat_item_type == 'ContainerGrammar':
                    (child_node, xml_child_node) = build_tree(
                        tree_node, xml_node, repeat_item, list_of_xml, target_dir, logger)
                    tree_node.add_child(child_node)


def tr(input_string):
    """ Return the input string after trimming within & outside the string."""
    return(' '.join(input_string.split()))


def handle_name(name_tag, target):
    """ Given a parsed Name tag, apply it to target node """
    name = name_tag.string.strip('"')
    csdl_name = get_valid_csdl_identifier(name)
    # do we need to change this? (errata)
    target.set('Name', csdl_name.split('.')[-1])
    return csdl_name


def handle_namespace(ns_tag, xml_node):
    """
    Handle 'namespace'
    """
    # disabled namespace
    xml_node.set('ns', ns_tag.arg)


def handle_prefix(prefix_tag, xml_node):
    """
    Handle 'prefix'
    """
    tag, name, semicolon = prefix_tag
    xml_node.set('Prefix', name.string.replace('"', '')) 


def handle_import(import_tag, xml_node):
    if len(import_tag.elements) > 2 and str(type(import_tag.elements[2])) == 'Prefix':  # A 'prefix' is present
        tag, name, prefix_tag = import_tag
        print(prefix_tag)
        brace, tag, prefix, semi, cbrace = prefix_tag
        prefix_string = prefix.string
    else:
        tag, name, semi_colon = import_tag
        prefix_string = None
    return name.string, prefix_string


def handle_revision(revision_tag, xml_node):
    """
    Handle 'revision'
    """
    revision_items = revision_tag.elements
    tag, date = tuple(revision_items[:2])
    inner_node = xml_convenience.add_annotation(xml_node,
                                     {'String':  date.string.strip('"'),
                                      'Term': redfishtypes.get_descriptive_properties_mapping('Revision')
                                      })
    for item in revision_items[2:]:
        for internal_item in item:
            item_type = str(type(internal_item))
            if item_type == 'OPENBRACE':
                continue
            elif item_type == 'CLOSEBRACE':
                continue
            elif item_type == "<REPEAT>":
                repeat_items = internal_item.elements
                for extra in repeat_items:
                    if str(type(extra)) == "Description":
                        handle_descriptor(extra, inner_node)
                    if str(type(extra)) == "Reference":
                        handle_reference(extra, inner_node)





def handle_descriptor(descriptor_tag, xml_node):
    descriptive_type = descriptor_tag.keyword
    value = descriptor_tag.arg 
    annotation = xml_convenience.add_annotation(xml_node,
                    {
                        'Term': redfishtypes.get_descriptive_properties_mapping(descriptive_type),
                        'String': value.replace('\n',' ')
                    })
    if descriptive_type == 'feature':
        for item in descriptor_tag.substmts:
            handle_descriptor(item, annotation)


# Handle the typedef statement
def handle_typedef(typedef_tag, schema_xml, module_xml):
    """
    Handle typedef statement.
    :param items: Grammar items.
    :param xml_parent: Node to which sub elements are to be added.
    """
    name, repeats = typedef_tag.arg, typedef_tag.substmts
    type_tag, desc, ref_tag = None, None, None
    for item in repeats:
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
        new_node.set('Name', get_valid_csdl_identifier(str(name)))
        if desc is not None:
            handle_descriptor(desc, new_node)
        if ref_tag is not None:
            handle_reference(ref_tag, new_node)
        for enum_tag in type_tag.substmts:
            member_node = SubElement(new_node, 'Member')
            member_name = enum_tag.arg
            member_node.set('Name', member_name)

            for extra in enum_tag.substmts:
                if extra.keyword == "description":
                    handle_descriptor(extra, member_node)
                elif extra.keyword == 'value':
                    member_node.set('Value', extra.arg) 

        schema_xml.append(new_node) 
        return str(name), new_node

    else: 
        new_node = Element('TypeDefinition')
        new_node.set('Name', get_valid_csdl_identifier(str(name)))
        if desc is not None:
            handle_descriptor(desc, new_node)
        if ref_tag is not None:
            handle_reference(ref_tag, new_node)
        simple_name, repeat_simple, = type_tag.arg, type_tag.substmts

        simple_name_string = simple_name.replace('"', '')

        new_node.set('UnderlyingType', redfishtypes.get_node_types_mapping(simple_name_string))

        if repeat_simple is not None:
            for item in repeat_simple:
                handle_metadata_grammar(item, new_node)
        schema_xml.append(new_node) 
        return str(name), new_node


def handle_uses(logger):
    logger.info(
        'Found uses statement. Please run a pre-processor to handle it. Ignoring uses statement')


def handle_metadata_grammar(metadata_grammar_tag, xml_node):
    """
    Handle metadata such as Range, Path, Bits, Base, Length, Min, Max
    Assumption is that only one of the above will be present.
    :param metadata_grammar_elements: Grammar elements
    :param xml_node:
    """
    metadata_type = metadata_grammar_tag.keyword.strip('"')

    term = redfishtypes.get_descriptive_properties_mapping(metadata_type)

    if term == 'type':  # ignore type within type
        pass
    else:
        for x in items:
            print(x)
        string = (metadata_type)
        xml_convenience.add_annotation(xml_node, {'Term': term, 'String': string})


def handle_type(type_tag, xml_node, parent_node, parent_entity, imports, types):
    """
    Handle 'type' statement 
    :param type_grammar_items: Grammar items within type definition in 
    YANG model
    :param xml_node: XML node to which sub elements are to be added.
    """
    # What are we?  Simple Type?  Get our info.
    tag, type_grammar = type_tag 
    if str(type(type_grammar)) == 'SimpleType':
        simple_name, colon = type_grammar
    elif str(type(type_grammar)) == 'SimpleTypeWithMetadata':
        simple_name, brace, repeat_simple, cbrace = type_grammar
    else:
        simple_name = None
    simple_name_string = "None" if simple_name is None else simple_name.string
    simple_name_string = simple_name_string.replace('"', '')
    # If there's an import, let's consider it ':'
    # If it's in the imports, then add the import
    # If it is a simple name already in types available, then put it in file
    if ':' in simple_name_string:
        importname = simple_name_string.split(':')[0]
        if importname in imports:
            xml_convenience.add_import(parent_node, imports[importname], importname if importname != imports[importname] else None)
    elif simple_name_string in types:
        namespace = parent_entity.attrib.get('Namespace')
        available_types = list()
        for ref in parent_node:
            if str(ref.tag) not in ['TypeDefinition', 'EnumType']:
                continue
            available_types.append(ref.attrib.get('Name'))
        if get_valid_csdl_identifier(simple_name_string) not in available_types:
            parent_node.append(types[simple_name_string])
        if namespace is None:
            print("Namespace shouldn't be none {}".format(parent_entity.attrib))
            print(get_valid_csdl_identifier(redfishtypes.types_mapping.get(simple_name_string, simple_name_string)))
        elif namespace is not "":
            namespace = namespace + "."
        xml_node.set('BaseType', str(namespace) + get_valid_csdl_identifier(redfishtypes.types_mapping.get(simple_name_string, simple_name_string)))
        return
    else:
        # must be a basic type?  if it isn't, we have a problem
        pass

    xml_node.set('Type', get_valid_csdl_identifier(redfishtypes.types_mapping.get(simple_name_string, simple_name_string)))
    # (todo, real type stuff, conflate with typedef)
    return
    
    var_type = str(type(type_grammar_items[1]))
    yang_type = None
    # Set some annotation properties because we can do it now. Other
    # option is to repeat the annotation statements in the if and else sections
    xml_node.set('Type', var_type)
    annotation = SubElement(xml_node, 'Annotation')
    annotation.set('Term', redfishtypes.get_descriptive_properties_mapping('YangType'))
    if var_type == 'EnumerationGrammar':
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
    else:
        # The var_type == 'SimpleTypeWithMetadata' or 'SimpleType':
        # Note : Since we have am OR grammar, item.elements[1] = GRAMMAR
        type_grammar = str(type(type_grammar_items[1]))
        primitive_yang_type = type_grammar_items[
            1].elements[0].string.strip('"')
        csdl_type = redfishtypes.types_mapping.get(
            primitive_yang_type, 'Yang.' + primitive_yang_type)
        yang_type = primitive_yang_type
        if (tree_node is not None) and (tree_node.get_type() == 'LeafListKeyword'):
            xml_node.set('Type', 'Collection(' + csdl_type + ')')
        else:  # Tree_node is None : RPC Leaf; Or type is Leaf
            xml_node.set('Type', csdl_type)
        if type_grammar == 'SimpleTypeWithMetadata':
            metadata_grammar = type_grammar_items[1].elements[2]
            metadata_grammar_type = str(type(metadata_grammar))
            handle_metadata_grammar(metadata_grammar, xml_node)
    annotation.set('String', yang_type)


def handle_rpc(rpc_tag, xml_node):
    """
    Handle RPC statement.
    """
    rpc_items = rpc_tag.elements
    for item in rpc_items:
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


def handle_reference(reference_tag, xml_node):
    """
    Handle 'reference'
    """
    name = reference_tag.arg
    xml_convenience.add_annotation(xml_node, {'Term': redfishtypes.get_descriptive_properties_mapping(
        'reference'), 'String': name})


def handle_unit(unit_tag, xml_node):
    """
    Handle 'unit'
    """
    items = unit_tag.elements
    xml_convenience.add_annotation(xml_node, {'Term': redfishtypes.get_descriptive_properties_mapping('Units'),
                              'String': items[1].string.strip('"')
                              }
                   )


def handle_default(default_tag, xml_node):
    """
    Handle 'default'
    """
    items = default_tag.elements
    xml_node.set('DefaultValue', items[1].string.strip('"'))




def handle_yang_version(version_tag, xml_node):
    """
    Handle 'yang_version'
    """
    yang_version_items = version_tag.elements
    xml_convenience.add_annotation(xml_node, {
        'Term': 'RedfishYang.yang_version',
        'String': yang_version_items[1].string.strip('"')}
    )


def handle_presence(presence_tag, xml_node):
    """
    Handle 'presence'
    """
    presence_elements = presence_tag.elements
    xml_convenience.add_annotation(xml_node, {
        'Term': redfishtypes.get_descriptive_properties_mapping('presence'),
        'String': presence_elements[1].string.strip('"').replace('\n','').strip('  ')
    })


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


def handle_unique(unique_key, xml_node):
    """
    Handle 'unique'
    """
    unique_items = unique_key.elements
    xml_convenience.add_annotation(xml_node, {
        'Term':  redfishtypes.get_descriptive_properties_mapping('unique'),
        'String': unique_items[1].string.strip('"')
    }
    )


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


def handle_when(when_tag, xml_node):
    """
    Handle 'when'
    """
    when_items = when_tag.elements
    xml_convenience.add_annotation(xml_node, {
        'Term': 'RedfishYang.when',
        'String': when_items[1].string.strip('"')
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


def handle_identity(identity_tag, xml_node):
    identity_elements = identity_tag.elements
    complex_node = xml_convenience.add_annotation(xml_node, {
                   'Term': 'RedfishYang.identity', 'String': identity_elements[1].string.strip('"')})
    for identity_item in identity_elements[2:]:
        identity_item_type = str(type(identity_item))
        if identity_item_type == '<REPEAT>':
            repeat_items = identity_item.elements
            for item in repeat_items:
                identity_item_type = str(type(item))
                if identity_item_type == 'Description':
                    description = (tr(item.elements[1].string)).strip('"')
                    xml_convenience.add_annotation(complex_node, {'Term': redfishtypes.get_descriptive_properties_mapping(
                        'description'), 'String': description})
                elif identity_item_type == 'Reference':
                    handle_reference(item, complex_node)
                elif identity_item_type == 'Status':
                    handle_status(item, complex_node)
                elif identity_item_type == 'Base':
                    string = item.elements[1].string.strip('"')
                    xml_convenience.add_annotation(complex_node, {'Term': redfishtypes.get_descriptive_properties_mapping('base'), 'String': string})


# handled ordered-by statement
def handle_orderedby(ordered_tag, xml_node):
    """
    Handle 'orderedby'
    """
    orderedby_elements = ordered_tag
    value = orderedby_elements[1].string.strip('"')
    xml_convenience.add_annotation(xml_node, {
        'Term': redfishtypes.get_descriptive_properties_mapping('ordered-by'),
        'EnumMember': 'RedfishYang.Ordered_by/' + value
    })


def handle_min_elements(min_tag, xml_node):
    """
    Handle 'min elements'
    """
    minelements = min_tag.elements
    value = minelements[1].string.strip('"')
    xml_convenience.add_annotation(xml_node, {
        'Term': redfishtypes.get_descriptive_properties_mapping('min-elements'),
        'RedfishYang.min_elements': value
    }
    )


def handle_max_elements(max_tag, xml_node):
    """ 
    Handle 'max elements'
    """
    maxelements = max_tag.elements
    value = maxelements[1].string.strip('"')
    xml_convenience.add_annotation(xml_node, {
        'Term': redfishtypes.get_descriptive_properties_mapping('max-elements'),
        'RedfishYang.max_elements': value
    }
    )



def handle_must(must_tag, xml_node):
    """
    Handle 'must' statement
    """
    must_elements = must_tag.elements
    must_annotation = xml_convenience.add_annotation(xml_node, {
        'Term': redfishtypes.get_descriptive_properties_mapping('must'),
        'String': must_elements[1].string.strip('"')
    })
    # The following constructs are equivalent
    #(must_elements[1])
    #(must_elements[1].string)
    #(must_elements[1].elements[0].string)

    if str(must_elements[2]) == ';':
        return
    print(str(must_elements[2]))
    items = must_elements[3].elements
    for item in items:
        # This is a short cut to handle the items. We know that the
        # substatement will be the first item and some string will be the second.
        # The only thing we have an explicit handler for is reference, and it is
        # not being used.
        term = item.elements[0].string.strip('"')
        string = item.elements[1].string.strip('"')
        xml_convenience.add_annotation(must_annotation,
                       {
                           'Term': redfishtypes.get_descriptive_properties_mapping(term),
                           'String': string
                       }
                       )


def handle_deviation(deviation_tag, xml_node):
    """
    Handle 'deviation'
    """
    deviation_items = deviation_tag.elements
    deviation_annotation = None
    for item in deviation_items:
        item_type = str(type(item))
        if item_type == 'DeviationValue':
            value = item.elements[0].string.strip('"')
            deviation_annotation = xml_convenience.add_annotation(xml_node,
                                                  {
                                                      'Term': redfishtypes.get_descriptive_properties_mapping('deviation'),
                                                      'String': value
                                                  })
        elif item_type == 'Reference':
            handle_reference(item, deviation_annotation)
        elif item_type == '<REPEAT>':
            repeat_items = item.elements
# Only 'deviate' can be part of deviation. so no need to check the type of the
# repeated item.
            for repeat_item in repeat_items:
                handle_deviate(repeat_item, deviation_annotation)


def handle_deviate(deviate_tag, xml_node):
    """
    Handle 'deviate'
    """
    deviate_items = deviate_tag.elements
    for item in deviate_items:
        item_type = str(type(item))
        if item_type == 'DeviateValue':
            value = item.elements[0].string.strip('"')
            xml_convenience.add_annotation(xml_node,
                           {
                               'Term': redfishtypes.get_descriptive_properties_mapping('deviate'),
                               'String': value

                           })
        elif item_type == 'Config':
            handle_config(item, xml_node)
        elif item_type == 'Default':
            handle_default(item, xml_node)
        elif item_type == 'Mandatory':
            handle_mandatory(item, xml_node)
        elif item_type == 'MinElements':
            handle_min_elements(item, xml_node)
        elif item_type == 'MaxElements':
            handle_max_elements(item, xml_node)
        elif item_type == 'Units':
            handle_unit(item, xml_node)
        elif item_type == 'Must':
            handle_must(item, xml_node)
        elif item_type == 'Unique':
            handle_unique(item, xml_node)
        elif item_type == 'Type':
            handle_type(item, xml_node)
        else:
            continue


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
                   'Term': 'RedfishYang.AnyxmlText', 'String': anyxml.string})

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
