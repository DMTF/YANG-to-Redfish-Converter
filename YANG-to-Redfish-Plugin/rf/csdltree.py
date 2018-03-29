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
# leaflist/leaf as one of their sub statements.

logger = None 

def setLogger(mylogger):
    global logger
    logger = mylogger


def createCollectionXML(name, prefix=None):
    collection_name = name + "Collection"
    collection_xml_root = xml_convenience.add_CSDL_Headers(None)

    collection_xml_root = xml_convenience.add_reference(collection_xml_root,
            "http://redfish.dmtf.org/schemas/v1/Resource_v1.xml",
            "Resource.v1_0_0", None )

    collection_xml_root = xml_convenience.add_reference(collection_xml_root,
            "http://redfish.dmtf.org/schemas/v1/" + prefix + name + "_v1.xml",
            prefix + name, str(name) )

    collection_data_services_node = SubElement(
        collection_xml_root, 'edmx:DataServices')
    collection_schema_node = SubElement(collection_data_services_node, 'Schema')
    collection_schema_node.set("xmlns", "http://docs.oasis-open.org/odata/ns/edm")
    # should this namespace be truncated as well? (errata)
    collection_schema_node.set("Namespace", prefix + collection_name)
    collection_target = SubElement(collection_schema_node, "EntityType")

    collection_target.set('Name', collection_name.split('.')[-1])
    collection_target.set('BaseType' ,"Resource.v1_0_0.ResourceCollection")
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
    nav_prop.set('Type', 'Collection(' + prefix + listname + '.' + listname + ')')
    nav_prop.set('Nullable', 'false')
    xml_convenience.add_annotation(nav_prop, {'Term':'OData.Permissions',
        'EnumMember':'OData.Permissions/Read'})
    xml_convenience.add_annotation(nav_prop, {'Term':'OData.Description', 'String':'Contains members of this collection.'})
    xml_convenience.add_annotation(nav_prop, {'Term':'OData.AutoExpandReferences'})
    return collection_xml_root


def create_xml_base(csdlname, prefix=None):
    main_node = xml_convenience.add_CSDL_Headers(True)
    entity_node = None
    # add refs to main, then add data services node
    data_services_node = Element('edmx:DataServices')
    schema_node = SubElement(data_services_node, 'Schema')
    schema_node.set(
        'Namespace', prefix + csdlname + ".v1_0_0")
    schema_node.set(
        'xmlns', 'http://docs.oasis-open.org/odata/ns/edm')
    # add in first schema
    schema_node_og = Element('Schema')
    schema_node_og.set('Namespace', prefix + csdlname)
    schema_node_og.set(
        'xmlns', 'http://docs.oasis-open.org/odata/ns/edm')
    data_services_node.insert(0, schema_node_og)

    schema1_entity = SubElement(schema_node_og, 'EntityType')
    schema1_entity.set('Name', csdlname.split('.')[-1])
    schema1_entity.set('BaseType', 'Resource.v1_0_0.Resource')
    schema1_entity.set(
        'Abstract', str(True))
    xml_convenience.add_annotation(schema1_entity, {
                   'Term': 'OData.Description', 'String': 'Parameters for {}'.format(csdlname)})
    xml_convenience.add_annotation(schema1_entity, {
                   'Term': 'OData.LongDescription', 'String': 'Parameters for {}'.format(csdlname)})
    xml_convenience.add_collection_annotation(schema1_entity, {"Term":
        "Capabilities.InsertRestrictions"}, {"Insertable": "false"})
    xml_convenience.add_collection_annotation(schema1_entity, {"Term":
        "Capabilities.UpdateRestrictions"}, {"Updatable": "false"})
    xml_convenience.add_collection_annotation(schema1_entity, {"Term":
        "Capabilities.DeleteRestrictions"}, {"Deletable": "false"})
    return main_node, schema_node, data_services_node

#=======================================================
# Recursive function to handle containment statements
# such as container, list, leaf, leaflist.
# Other statements are handed off to respective handlers - handlers.handle_XXXXX
# defined in this file and in statement_handlers.py.

def build_tree(yang_item, list_of_xml, xlogger, prefix="", topleveltypes=None, toplevelimports=None, parent=None, parent_schema=None, parent_entity=None):
    seg_type = yang_item.keyword
    name = yang_item.arg
    if topleveltypes == None:
        topleveltypes = dict()
    if toplevelimports == None:
        toplevelimports = dict()

    if seg_type in ['module', 'container', 'list']:
        csdlname = handlers.get_valid_csdl_identifier(name.strip('"'))
        main_node, schema_node, data_services_node = create_xml_base(csdlname, prefix)
        main_node.insert(0, data_services_node)
        member = redfishtypes.get_node_types_mapping(seg_type)
        entity_node = Element("EntityType")
        entity_node.set('Name', csdlname.split('.')[-1])
        entity_node.set('BaseType', prefix + csdlname.split('.')[-1] + '.' + csdlname.split('.')[-1])
        xml_convenience.add_annotation(
            schema_node, {'Term': 'RedfishYang.NodeType', 'EnumMember': member})
        filename = csdlname + '_v1.xml'

        if hasattr(yang_item, 'i_children'):
            content = yang_item.i_children if len(yang_item.i_children) > 0 else []
        else:
            content = yang_item.substmts

        for item in content:
            build_tree_repeat(item, schema_node, entity_node, main_node, list_of_xml, logger, prefix + csdlname + '.', topleveltypes=topleveltypes, toplevelimports=toplevelimports)

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

        return main_node

    if seg_type in ['leaf']:
        if hasattr(yang_item, 'i_children'):
            content = yang_item.i_children if len(yang_item.i_children) > 0 else []
        else:
            content = yang_item.substmts
        csdlname = handlers.get_valid_csdl_identifier(name)
        member = redfishtypes.get_node_types_mapping(seg_type)

        target = Element("Property")
        xml_convenience.add_annotation(
            target, {'Term': 'RedfishYang.NodeType', 'EnumMember': member})
        target.set('Name', csdlname)
        for item in content:
            build_tree_repeat(item, target, parent_entity, parent, list_of_xml, logger, prefix + csdlname + '.', topleveltypes=topleveltypes, toplevelimports=toplevelimports)
        xml_convenience.add_annotation(
            target, {'Term': 'OData.Permissions', 'EnumMember': 'OData.Permission/Read'})

        return target

    if seg_type in ['leaflist']:
        if hasattr(yang_item, 'i_children'):
            content = yang_item.i_children if len(yang_item.i_children) > 0 else []
        else:
            content = yang_item.substmts
        csdlname = handlers.get_valid_csdl_identifier(name)
        member = redfishtypes.get_node_types_mapping(seg_type)

        prop_node = Element("Property")
        prop_node.set(
            'Name', csdlname)
        prop_node.set(
            'BaseType', 'Collection({}.{})'.format(prefix + "v1_0_0", csdlname))
        xml_convenience.add_annotation(
            prop_node, {'Term': 'RedfishYang.NodeType', 'EnumMember': member})
        xml_convenience.add_annotation(prop_node, {"Term": "OData.LongDescription",
                "String": "List of the type {}".format(csdlname)}
                )
        for item in content:
            build_tree_repeat(item, prop_node, parent_entity, parent_schema, list_of_xml, logger, prefix + csdlname + '.', topleveltypes=topleveltypes, toplevelimports=toplevelimports)
        xml_convenience.add_annotation(
                prop_node, {'Term': 'OData.Permissions', 'EnumMember': 'OData.Permission/Read'})
        return prop_node
    return None





def build_tree_repeat(yang_item, target, target_entity=None, target_parent=None, list_of_xml=None, xlogger=None, prefix='', topleveltypes=None, toplevelimports=None, additional_tags=None):
    # REPEAT(SubmoduleGrammar |  Namespace | AnyXML | YangVersion | Prefix | Import | Include | Organization | Contact | Description | RevisionGrammar, min=0),
    # REPEAT(Augment | Grouping | Identity | ContainerGrammar | ChoiceGrammar |
    #      RpcGrammar | Feature | TypedefGrammar | Deviation | Notification, min=0),
    # target_entity = tag of entitytype
    # target = tag of current target
    # target_parent = tag of its parent


    if topleveltypes is None:
        topleveltypes = dict()
    if toplevelimports is None:
        toplevelimports = dict()
    if additional_tags is None:
        additional_tags = list()

    yang_item = yang_item
    yang_keyword = yang_item.keyword
    yang_arg = yang_item.arg.replace('\n',' ') if yang_item.arg is not None else '-'
    if hasattr(yang_item, 'i_children'):
        yang_children = yang_item.i_children if len(yang_item.i_children) > 0 else []
    else:
        yang_children = yang_item.substmts

    logger.info('Handling repeat item: ' + str(yang_keyword))
    # print(yang_keyword)
    # print('\t', yang_arg)
    if yang_arg is None or type(yang_keyword) == tuple:
        input("Uhh")

    if yang_keyword == 'import': 
        import_name, prefix, date = yang_arg, None, None
        for item in yang_children:
            if item.keyword == "prefix":
                prefix = item.arg  
            if item.keyword == "revision-date":
                date = item.arg  
        toplevelimports[prefix if prefix not in [None, ''] else import_name] = import_name

    elif yang_keyword in ["typedef"]:
        result = handlers.handle_typedef(yang_keyword, yang_arg, yang_children, target, target_parent)
        if result is not None:
            type_name, type_node = result
            topleveltypes[type_name] = type_node

    elif yang_keyword in ['type']:
        handlers.handle_type(yang_item, target, target_parent, target_entity, imports=toplevelimports, types=topleveltypes)

    elif yang_keyword in ["enum"]:
        annotation = handlers.handle_enum(yang_keyword, yang_arg, yang_children, target)
    
    elif yang_keyword in ['choice']:
        annotation = handlers.handle_choice(yang_keyword, yang_arg, yang_children, target, target_entity, target_parent, list_of_xml, toplevelimports, topleveltypes, prefix)

    # elif yang_keyword in ['rpc']:
    #    annotation = handlers.handle_rpc(yang_keyword, yang_arg, yang_children, target, target_entity, target_parent, list_of_xml, toplevelimports, topleveltypes, prefix)

    elif yang_keyword in ["namespace", "prefix", "value"]:
        annotation = handlers.handle_generic_modifier(yang_keyword, yang_arg, target)

    elif (yang_keyword == 'list' or yang_keyword == 'container'):
        this_node = build_tree(yang_item, list_of_xml, logger, prefix, topleveltypes=topleveltypes, toplevelimports=toplevelimports)

        name = yang_arg
        if hasattr(yang_item, 'i_children'):
            content = yang_item.i_children if len(yang_item.i_children) > 0 else []
        else:
            content = []
        csdlname = handlers.get_valid_csdl_identifier(name)

        navigation_property = SubElement(
            target_entity, 'NavigationProperty')
        
        # Handle Container Grammar
        if yang_keyword in ['container']:
            member = redfishtypes.get_node_types_mapping('ContainerGrammar')
            tname = csdlname.split('.')[-1] + 'Container'
            navigation_property.set('Name', tname)
            tname = csdlname.split('.')[-1]
            navigation_property.set('Type', tname + '.' + tname)

        # Handle List Grammar
        if yang_keyword in ['list']:
            member = redfishtypes.get_node_types_mapping('ListGrammar')
            tname = csdlname.split('.')[-1]
            navigation_property.set('Name', tname)
            navigation_property.set('Type', tname + '.' + tname)
            csdlname = csdlname + 'Collection'

        navigation_property.set('ContainsTarget', str(True))
        filename = prefix + csdlname + '_v1.xml'

        alias = csdlname.split('.')[-1]
        xml_convenience.add_reference(target_parent,
            "http://redfish.dmtf.org/schemas/v1/{}".format(filename),
            "{}{}".format(prefix, alias), alias)
        # At the end of the grammar, modify outside nav property
        xml_convenience.add_annotation(navigation_property, {
                'Term': 'OData.Permissions',
                'EnumMember': 'OData.Permissions/Read'
                })
        xml_convenience.add_annotation(navigation_property, {
                'Term': 'OData.Description',
                'String': 'Navigation property that points to a resource of {}.'.format(str(csdlname))
                })
        xml_convenience.add_annotation(navigation_property, {
                'Term': 'OData.LongDescription',
                'String': 'Automatically generated.'
                })
        xml_convenience.add_annotation(navigation_property, {
                'Term': 'AutoExpandReferences',
                })
        return navigation_property

    elif yang_keyword == 'leaf' or yang_keyword == 'leaflist':
        this_node = build_tree(yang_item, list_of_xml, logger, prefix=prefix, parent=target_parent, parent_schema=target, parent_entity=target_entity, topleveltypes=topleveltypes, toplevelimports=toplevelimports)
        target_entity.append(this_node)
        return this_node

    else:
        if yang_keyword in ['case', 'submodule', 'include', 'augment', 'rpc', 'uses']:
            logger.debug('Ignored tag: {}'.format(yang_keyword))
            yang_children = []
        annotation = handlers.handle_generic(yang_keyword, yang_arg, yang_children, target)

    return

    if yang_keyword == 'anyxml': # fix
        handlers.handle_anyxml(yang_item, target, anyxml_count)
        anyxml_count = anyxml_count + 1

    # module_content
    elif yang_keyword == 'Augment':
        logger.debug("Handling augment")
        xml_nodes_to_annotate = []
        xml_annotations = []
        augment_name = None
        augment_xml_node = xml_convenience.add_CSDL_Headers(None)
        main_node = SubElement(
            augment_xml_node, 'Main')
        ref_node = SubElement(
            augment_xml_node, 'Refs')
        entity_node = SubElement(
            augment_xml_node, 'Entitys')
        xml_content = XMLContent()
        xml_content.set_xml(augment_xml_node)
        list_of_xml.append(xml_content)
        for item in yang_item.elements:
            item_type = str(type(item))
            if item_type == 'AugmentName':
                augment_name = item.elements[0].string.replace('"','').replace(" ",":").replace('/','_')
                logger.debug("Handling augment : " + augment_name)
                print("Handling augment : " + augment_name)
                main_node.set('target', augment_name)
                xml_content.set_filename("augment" + augment_name + '.xml')
            elif item_type == '<REPEAT>':
                yang_items_inner = item.elements
                for yang_item_inner in yang_items_inner:
                    yang_keyword_inner = str(type(yang_item_inner))
                    if yang_keyword_inner in ['When', 'Description']:
                        xml_node = Element('Annotation')
                        xml_node.set(
                            'Term', redfishtypes.get_descriptive_properties_mapping(yang_keyword_inner))
                        xml_node.set('String',
                            str(yang_item_inner.elements[1]).strip('"'))
                        xml_annotations.append(xml_node)
                    else:
                        new_list_of_xml = []
                        this_node = build_tree_repeat(yang_item_inner, entity_node, main_node, ref_node, new_list_of_xml, logger, prefix, topleveltypes, toplevelimports)
                        for xml in new_list_of_xml:
                            xml.filename = "augment" + str(augment_name).replace('/','_') + xml.filename
                            list_of_xml.append(xml)
                        if this_node is not None:
                            xml_nodes_to_annotate.append(this_node)
        for node in xml_nodes_to_annotate:
            augment_annotation = Element('Annotation')
            augment_annotation.set(
                'Term', redfishtypes.get_descriptive_properties_mapping('augment'))
            augment_annotation.set('String', augment_name)

            for annotation in xml_annotations:
                augment_annotation.append(annotation)
            node.append(augment_annotation)
        for x in augment_xml_node:
            print(x)

    elif yang_keyword == 'Grouping':
        handlers.handle_grouping(yang_item, target,
                        target_parent, list_of_xml, '', logger)

    elif yang_keyword == 'Identity':
        handlers.handle_identity(yang_item, target)

    elif yang_keyword == 'Presence':
        handlers.handle_presence(yang_item, target)

    elif yang_keyword == 'Config':
        boolean = handlers.handle_config(yang_item, target)
        permission = xml_convenience.add_annotation(
                target, {'Term': 'OData.Permissions', 'EnumMember': 'OData.Permission/Read{}'.format('' if boolean == "true" else 'Write')})
        # use this to make permissions correct
        # pass in permissions tag??

    elif yang_keyword == 'Default':
        handlers.handle_default(yang_item, target)

    elif yang_keyword == 'Units':
        handlers.handle_unit(yang_item, target)

    elif yang_keyword == 'Mandatory':
        handlers.handle_mandatory(yang_item, target)

    elif yang_keyword == 'Key':
        handlers.handle_key(yang_item, target)

    elif yang_keyword == 'Unique':
        handlers.handle_unique(yang_item, target)

    elif (yang_keyword == 'RpcGrammar'): # fix
        logger.debug('Ignored tag: {}'.format(yang_keyword))
        return None
        handlers.handle_rpc(yang_item, target)

    elif yang_keyword == 'Unmapped':
        handlers.handle_unmapped(yang_item, target)

    elif yang_keyword == 'Notification':
        logger.debug('Ignored tag: {}'.format(yang_keyword))
        return None
        (child_node, xml_child_node) = build_tree(
            target, target_parent, yang_item.elements, list_of_xml, target_dir, logger)
        tree_node.add_child(child_node)

    elif yang_keyword == 'Extension':
        handlers.handle_extension(yang_item, target)
        
    else:
        logger.warning(
            "Unhandled Item: {0}".format(yang_keyword))
    return None
