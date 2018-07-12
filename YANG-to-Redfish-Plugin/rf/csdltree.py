# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

import rf.redfishtypes as redfishtypes
import rf.statement_handlers as handlers
import rf.xml_convenience as xml_convenience
from rf.xml_content import XMLContent
from xml.etree.ElementTree import Element, SubElement

# This file contains the build_tree function and handlers
# for YANG statements that would result in the build_tree being
# called - i.e Yang statements which could have container/list/
# leaf-list/leaf as one of their sub statements.

logger = None
current_xml_top = []


def setLogger(mylogger):
    global logger
    logger = mylogger



def createCollectionXML(name, prefix=''):
    collection_name = name + "Collection"

    collection_xml_root = xml_convenience.add_CSDL_Headers(None)
    xml_convenience.add_reference(
        collection_xml_root, "http://redfish.dmtf.org/schemas/v1/Resource_v1.xml", "Resource.v1_0_0", None)
    xml_convenience.add_reference(
        collection_xml_root, "http://redfish.dmtf.org/schemas/v1/" + prefix + name + "_v1.xml", prefix + name, str(name))

    collection_data_services_node = SubElement(
        collection_xml_root, 'edmx:DataServices')
    collection_schema_node = SubElement(collection_data_services_node, 'Schema')
    collection_schema_node.set("xmlns", "http://docs.oasis-open.org/odata/ns/edm")
    collection_schema_node.set("Namespace", prefix + collection_name)

    xml_convenience.add_annotation(collection_schema_node, {"Term": "Redfish.OwningEntity", "String": "DMTF"})

    collection_target = SubElement(collection_schema_node, "EntityType")
    collection_target.set('Name', collection_name.split('.')[-1])
    collection_target.set('BaseType', "Resource.v1_0_0.ResourceCollection")

    xml_convenience.add_annotation(collection_target, {"Term": "OData.Description", 
        "String": "A Collection of " + name + " resource instances." 
        })
    xml_convenience.add_collection_annotation(collection_target, {"Term":
        "Capabilities.InsertRestrictions"}, {"Insertable": "false"})
    xml_convenience.add_collection_annotation(collection_target, {"Term":
        "Capabilities.UpdateRestrictions"}, {"Updatable": "false"})
    xml_convenience.add_collection_annotation(collection_target, {"Term":
        "Capabilities.DeleteRestrictions"}, {"Deletable": "false"})

    nav_prop = SubElement(collection_target, 'NavigationProperty')
    nav_prop.set('Name', 'Members') 
    listname = name.split('.')[-1]
    # should this be without the namespace at all (errata)
    nav_prop.set('Type', 'Collection(' + listname + '.' + listname + ')')
    xml_convenience.add_annotation(nav_prop, {'Term':'OData.Permissions',
        'EnumMember':'OData.Permissions/Read'})
    xml_convenience.add_annotation(nav_prop, {'Term':'OData.Description', 'String':'Contains members of this collection.'})
    xml_convenience.add_annotation(nav_prop, {'Term':'OData.AutoExpandReferences'})
    return collection_xml_root


def create_xml_base(csdlname, prefix=''):
    main_node = xml_convenience.add_CSDL_Headers(True)
    xml_convenience.add_reference(main_node,
            "http://redfish.dmtf.org/schemas/v1/Resource_v1.xml",
            "Resource.v1_0_0", None )
    entity_node = None
    # add refs to main, then add data services node
    data_services_node = Element('edmx:DataServices')
    schema_node = SubElement(data_services_node, 'Schema')
    schema_node.set(
        'Namespace', prefix + csdlname + ".v1_0_0")
    schema_node.set(
        'xmlns', 'http://docs.oasis-open.org/odata/ns/edm')
    xml_convenience.add_annotation(schema_node, {"Term":
        "Redfish.OwningEntity", "String": "DMTF"})
    # add in first schema
    schema_node_og = Element('Schema')
    schema_node_og.set('Namespace', prefix + csdlname)
    schema_node_og.set(
        'xmlns', 'http://docs.oasis-open.org/odata/ns/edm')
    xml_convenience.add_annotation(schema_node_og, {"Term":
        "Redfish.OwningEntity", "String": "DMTF"})
    data_services_node.insert(0, schema_node_og)

    schema1_entity = SubElement(schema_node_og, 'EntityType')
    schema1_entity.set('Name', csdlname.split('.')[-1])
    schema1_entity.set('BaseType', 'Resource.v1_0_0.Resource')
    schema1_entity.set(
        'Abstract', 'true')
    xml_convenience.add_annotation(schema1_entity, {
                   'Term': 'OData.Description', 'String': 'Parameters for {}.'.format(csdlname)})
    xml_convenience.add_annotation(schema1_entity, {
                   'Term': 'OData.LongDescription', 'String': 'Parameters for {}.'.format(csdlname)})
    xml_convenience.add_collection_annotation(schema1_entity, {"Term":
        "Capabilities.InsertRestrictions"}, {"Insertable": "false"})
    xml_convenience.add_collection_annotation(schema1_entity, {"Term":
        "Capabilities.UpdateRestrictions"}, {"Updatable": "false"})
    xml_convenience.add_collection_annotation(schema1_entity, {"Term":
        "Capabilities.DeleteRestrictions"}, {"Deletable": "false"})
    return main_node, schema_node, data_services_node

#=======================================================
# Recursive function to handle containment statements
# such as container, list, leaf, leaf-list.
# Other statements are handed off to respective handlers - handlers.handle_XXXXX
# defined in this file and in statement_handlers.py.

def build_tree(yang_item, list_of_xml, xlogger, prefix="", topleveltypes=None, toplevelimports=None, parent=None, parent_schema=None, parent_entity=None):
    seg_type = yang_item.keyword
    name = yang_item.arg
    if topleveltypes == None:
        topleveltypes = dict()
    if toplevelimports == None:
        toplevelimports = dict()

    if seg_type in ['module','submodule', 'container', 'list', 'grouping']:
        csdlname = handlers.get_valid_csdl_identifier(name)

        main_node, schema_node, data_services_node = create_xml_base(csdlname, prefix)
        main_node.insert(0, data_services_node)

        entity_node = Element("EntityType")
        entity_node.set('Name', csdlname.split('.')[-1])
        entity_node.set('BaseType', prefix + csdlname.split('.')[-1] + '.' + csdlname.split('.')[-1])

        handlers.handle_generic_node('leaf', seg_type, entity_node)

        filename = csdlname + '_v1.xml'

        if hasattr(yang_item, 'i_children'):
            content = yang_item.i_children if len(yang_item.i_children) > 0 else []
        content = yang_item.substmts

        current_xml_top.append(main_node)

        for item in content:
            build_tree_repeat(item, schema_node, entity_node, main_node, list_of_xml, logger, prefix + csdlname + '.', topleveltypes=topleveltypes, toplevelimports=toplevelimports)
        handlers.collectAnnotations(schema_node)
        handlers.collectAnnotations(entity_node)
        handlers.collectAnnotations(main_node)
        

        if seg_type in ['module']:
            # what is this in particular (errata)
            prefix = ""

        if seg_type in ['container']:
            prefix = prefix if prefix is not None else ""
            
        if seg_type in ['list']:
            prefix = prefix if prefix is not None else ""

            collection_node = createCollectionXML(csdlname, prefix)
            ccsdlname = csdlname + 'Collection'
            cfilename = prefix + ccsdlname + '_v1.xml'
            xml_content = XMLContent()
            xml_content.set_filename(cfilename)
            xml_content.set_xml(collection_node)
            list_of_xml.append(xml_content)

        filename = prefix + filename
        
        schema_node.append(entity_node)
        main_node.remove(data_services_node)
        main_node.append(data_services_node)
        xml_content = XMLContent()
        xml_content.set_filename(filename)
        xml_content.set_xml(main_node)
        list_of_xml.append(xml_content)

        current_xml_top.pop()

        return main_node

    if seg_type in ['leaf', 'leaf-list', 'notification', 'anyxml']:
        if hasattr(yang_item, 'i_children'):
            content = yang_item.i_children if len(yang_item.i_children) > 0 else []
        content = yang_item.substmts
        csdlname = handlers.get_valid_csdl_identifier(name)

        prop_node = Element("Property")
        prop_node.set('Name', handlers.get_valid_csdl_identifier(name))
        our_parent = parent

        if seg_type == 'leaf-list':
            prop_node.set(
                'Type', 'Collection({}.{})'.format(prefix + "v1_0_0", csdlname))
            xml_convenience.add_annotation(prop_node, {"Term": "OData.LongDescription",
                    "String": "List of the type {}.".format(csdlname)}
                    )
            our_parent = parent_schema

        if seg_type == 'anyxml':
            prop_node.set('Type', redfishtypes.types_mapping[seg_type] )

        if seg_type == 'notification':
            prop_node = Element("EntityType")
            prop_node.set('Name', handlers.get_valid_csdl_identifier(name))
            prop_node.set('BaseType', 'Resource.v1_0_0.Resource') 
        

        handlers.handle_generic_node('leaf', seg_type, prop_node)

        for item in content:
            build_tree_repeat(item, prop_node, parent_entity, parent_schema, list_of_xml, logger, prefix + csdlname + '.', topleveltypes=topleveltypes, toplevelimports=toplevelimports)
        xml_convenience.add_annotation(
            prop_node, {'Term': 'OData.Permissions', 'EnumMember': 'OData.Permission/Read'})
        handlers.collectAnnotations(prop_node)
        handlers.collectAnnotations(parent_entity)
        handlers.collectAnnotations(parent_schema)

        return prop_node

    return None


def build_tree_repeat(yang_item, target, target_entity=None, target_parent=None, list_of_xml=None, xlogger=None, prefix='', topleveltypes=None, toplevelimports=None, additional_tags=None):

    if topleveltypes is None:
        topleveltypes = dict()
    if toplevelimports is None:
        toplevelimports = dict()
    if additional_tags is None:
        additional_tags = list()

    yang_item = yang_item
    yang_keyword = yang_item.keyword
    yang_raw_keyword = yang_item.raw_keyword
    yang_arg = yang_item.arg.replace('\n', ' ') if yang_item.arg is not None else ''

    if hasattr(yang_item, 'i_children'):
        yang_children = yang_item.i_children if len(yang_item.i_children) > 0 else []
    yang_children = yang_item.substmts

    logger.info('Handling repeat item: ' + str(yang_keyword))
    # print(yang_keyword)
    # print('\t', yang_arg)

    if yang_keyword in ['import', 'include']:
        import_name, prefix, date = yang_arg, None, None
        for item in yang_children:
            if item.keyword == "prefix":
                prefix = item.arg
            if item.keyword == "revision-date":
                date = item.arg  
        toplevelimports[prefix if prefix not in [None, ''] else import_name] = import_name

    elif yang_keyword in ['typedef']:
        result = handlers.handle_typedef(yang_keyword, yang_arg, yang_children, target, target_parent)
        if result is not None:
            type_name, type_node = result
            topleveltypes[type_name] = type_node

    elif yang_keyword in ['type']:
        annotation = handlers.handle_type(yang_item, target, target_parent, target_entity, imports=toplevelimports, types=topleveltypes)

    elif yang_keyword in ["enum"]:
        annotation = handlers.handle_enum(yang_keyword, yang_arg, yang_children, target)

    elif yang_keyword in ['choice']:
        annotation = handlers.handle_choice(yang_keyword, yang_arg, yang_children, target, target_entity, target_parent, list_of_xml, toplevelimports, topleveltypes, prefix)

    # elif yang_keyword in ['rpc']:
    #    annotation = handlers.handle_rpc(yang_keyword, yang_arg, yang_children, target, target_entity, target_parent, list_of_xml, toplevelimports, topleveltypes, prefix)

    elif yang_keyword in ["namespace", "prefix", "value", "default"]:
        annotation = handlers.handle_generic_modifier(yang_keyword, yang_arg, target)

    elif yang_keyword in ["container", "list"]:
        this_node = build_tree(yang_item, list_of_xml, logger, prefix, topleveltypes=topleveltypes, toplevelimports=toplevelimports)

        name = yang_arg
        csdlname = handlers.get_valid_csdl_identifier(name)

        navigation_property = SubElement(target_entity, 'NavigationProperty')

        # Handle Container Grammar
        if yang_keyword in ['container']:
            tname = csdlname.split('.')[-1] + 'Container'
            navigation_property.set('Name', tname)
            tname = csdlname.split('.')[-1]
            navigation_property.set('Type', tname + '.' + tname)

        # Handle List Grammar
        if yang_keyword in ['list']:
            csdlname = csdlname + 'Collection'
            tname = csdlname.split('.')[-1]
            navigation_property.set('Name', tname)
            navigation_property.set('Type', tname + '.' + tname)

        navigation_property.set('ContainsTarget', 'true')
        filename = prefix + csdlname + '_v1.xml'

        alias = csdlname.split('.')[-1]
        xml_convenience.add_reference(target_parent, "http://redfish.dmtf.org/schemas/v1/{}".format(filename), "{}{}".format(prefix, alias), alias)
        # At the end of the grammar, modify outside nav property
        xml_convenience.add_annotation(navigation_property, {'Term': 'OData.Permissions', 'EnumMember': 'OData.Permissions/Read'})
        xml_convenience.add_annotation(navigation_property, {'Term': 'OData.Description', 'String': 'Navigation property that points to a resource of {}.'.format(str(csdlname))})
        xml_convenience.add_annotation(navigation_property, {'Term': 'OData.LongDescription', 'String': 'Automatically generated.'})
        xml_convenience.add_annotation(navigation_property, {'Term': 'OData.AutoExpandReferences'})
        return navigation_property

    elif yang_keyword in ['leaf', 'leaf-list', 'grouping', 'notification', 'anyxml']:
        this_node = build_tree(yang_item, list_of_xml, logger, prefix=prefix, parent=target_parent, parent_schema=target, parent_entity=target_entity, topleveltypes=topleveltypes, toplevelimports=toplevelimports)
        if yang_keyword in ['grouping']:
            handlers.handle_generic(yang_keyword, yang_arg, yang_children, target, generic=True, keyword_raw=yang_raw_keyword)
        if yang_keyword in ['notification']:
            target.append(this_node)
        else:
            target_entity.append(this_node)
        return this_node

    elif yang_keyword in redfishtypes.enum_mapping:
        handlers.handle_generic_node(yang_keyword, yang_arg, target)
    else:
        if yang_keyword in ['case', 'include', 'rpc', 'uses', 'choice', 'augment', 'action']:
            logger.debug('Tag being defaulted {}'.format(yang_keyword))
            handlers.handle_generic(yang_keyword, yang_arg, yang_children, target, generic=True, keyword_raw=yang_raw_keyword)
        else:
            handlers.handle_generic(yang_keyword, yang_arg, yang_children, target, keyword_raw=yang_raw_keyword)

    return
