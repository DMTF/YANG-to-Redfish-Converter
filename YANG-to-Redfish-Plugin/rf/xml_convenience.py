# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/main/LICENSE.md

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from rf.redfishtypes import get_valid_csdl_identifier

def add_import(xml_node, import_value, alias, namespace=None):
    """
    Add import stament node into XML.
    :param xml_node:Parent node to which 'import' node must be added.
    :param import_value: The name of the imported file
    :param alias: Optional alias for the imported file.
    """
    uri = 'http://redfish.dmtf.org/schemas/v1/' + import_value + "_v1.xml"
    for ref in xml_node:
        if 'Reference' not in str(ref.tag):
            continue
        uri_old = ref.attrib.get('Uri')
        if uri_old == uri:
            return None
    namespace = import_value if not namespace else namespace
    return add_reference(xml_node, uri, namespace, alias)


def add_reference(xml_node, uri, namespace, alias=None, version=None):
    """
    Add "edmx:Reference" node to XML.
    :param xml_node:Parent node to which reference  node must be added.
    :param uri: URI which will be added as the reference
    :param namespace: XML namespace or namespaces
    :param alias: Optional alias
    """
    if uri in ['', None]:
        uri = 'http://redfish.dmtf.org/schemas/v1/' + namespace + "_v1.xml"
    ref = Element('edmx:Reference')
    ref.set('Uri', uri)
    include = SubElement(ref, 'edmx:Include')
    if alias is not None:
        include.set('Alias', alias)
    if version:
        include.set('Namespace', namespace + '.' + version)
    else:
        include.set('Namespace', namespace)
    if xml_node is not None:
        xml_node.insert(0, ref)
    return ref


def add_references(xml_node, uri, entries):
    """
    Add "edmx:Reference" node to XML.
    :param xml_node: Parent node to which reference  node must be added.
    :param uri: URI which will be added as the reference
    :param entries: Dictionary of namespace-alias pairs
    """
    ref = SubElement(xml_node, 'edmx:Reference')
    ref.set('Uri', uri)
    for namespace, alias in entries.items():
        include = SubElement(ref, 'edmx:Include')
        if alias not in [None, '']:
            include.set('Alias', alias)
        include.set('Namespace', namespace)
    return xml_node


def add_list_reference(xml_node, uri, namespace, alias):
    ref = SubElement(xml_node, 'edmx:Reference')
    ref.set('Uri', uri)
    ref.set('Namespace' , namespace + '.xml')
    include = SubElement(ref, 'edmx:Include')
    if alias is not None:
        include.set('Alias', alias)
    if namespace is not None:
        include.set('Namespace', namespace)
    return xml_node


def create_Base_Xml():
    xml_node = Element('edmx:Edmx')
    xml_node.set('Version', '4.0')
    xml_node.set('xmlns:edmx', 'http://docs.oasis-open.org/odata/ns/edmx')
    return xml_node

def add_CSDL_Headers(is_singleton=False):
    """
    Add standard CSDL tags/references which are common across all the CSDL
    XML files.
    :param xml_node:Parent node to which headers must be added.
    """
    xml_node = create_Base_Xml()

    add_reference(xml_node,
            'http://docs.oasis-open.org/odata/odata/v4.0/errata03/csd01/complete/vocabularies/Org.OData.Core.V1.xml',
            'Org.OData.Core.V1', 'OData')
    add_reference(xml_node,
            'http://docs.oasis-open.org/odata/odata/v4.0/errata03/csd01/complete/vocabularies/Org.OData.Capabilities.V1.xml',
            'Org.OData.Capabilities.V1', 'Capabilities')
    add_references(xml_node,
            'http://redfish.dmtf.org/schemas/v1/RedfishExtensions_v1.xml',
            {'RedfishExtensions.v1_0_0': 'Redfish'})
    if is_singleton:
        nspaces = {'RedfishExtensions.v1_0_0': 'Redfish', 'Validation.v1_0_0': 'Validation'}
        add_reference(xml_node,
                'http://redfish.dmtf.org/schemas/v1/RedfishYangExtensions_v1.xml',
                      'RedfishYangExtensions.v1_0_0', 'RedfishYang')
    return xml_node


def add_annotation(xml_node, key_values):
    """
    Add node of type "Annotation" to the XML
    :param xml_node: Node to which Annotations have to be addeed.
    :param key_values: Key value pairs which will be used to create the
    annotation entries.
    """
    if xml_node is None:
        return Element('Annotation', key_values)
    annotation = SubElement(xml_node, 'Annotation')
    for key in key_values.keys():
        annotation.set(key, key_values[key])
    return annotation


def add_collection_annotation(xml_node, key_values, record_props):
    annotation = SubElement(xml_node, 'Annotation')
    for key in key_values.keys():
        annotation.set(key, key_values[key])
    record = SubElement(annotation, 'Record')
    for key in record_props.keys():
        record_property =  SubElement(record, "PropertyValue")
        record_property.set('Property', key)
        record_property.set('Bool', record_props[key])
    return annotation


def createExtensionsXML(name, types, xml_node = None, owner='TBD', release='TBD'):
    if xml_node is None:
        xml_node = create_Base_Xml()

        add_reference(xml_node,
                                      'http://docs.oasis-open.org/odata/odata/v4.0/errata03/csd01/complete/vocabularies/Org.OData.Core.V1.xml',
                                      'Org.OData.Core.V1', 'OData')

        extension_data_services_node = SubElement(
            xml_node, 'edmx:DataServices')
        extension_schema_node = SubElement(extension_data_services_node, 'Schema')
        extension_schema_node.set("xmlns", "http://docs.oasis-open.org/odata/ns/edm")
        extension_schema_node.set("Namespace", name + 'Extensions.v1_0_0')

        add_annotation(extension_schema_node, {"Term": "Redfish.OwningEntity", "String": owner})
        add_annotation(extension_schema_node, {"Term": "OData.LongDescription", "String": "The CSDL Terms, Type Definitions, and Enumerations defined in this schema section shall be interpreted as defined in RFC6020."})
    else:
        extension_schema_node = xml_node


    extension_target = SubElement(extension_schema_node, "Term")
    extension_target.set('Name', "YangType")
    extension_target.set('Type', name + '.v1_0_0.YangTypes')

    add_annotation(extension_target,
                                   {"Term": "OData.Description",
                                    "String": "A extension of " + name + " resource instances."
                                    })

    extension_target = SubElement(extension_schema_node, "EnumType")
    extension_target.set('Name', 'YangTypes')

    combinedtypes = {}
    combinedtypes.update(types)

    for item in list(sorted(types.keys())):
        og_item, item = item, get_valid_csdl_identifier(item)
        member_node = SubElement(extension_target, 'Member')
        member_node.set('Name', item)
        # extension_term = SubElement(extension_schema_node, "Term")
        # extension_term.set('Name', item)
        # extension_term.set('Type', combinedtypes[og_item])

    return xml_node


def createCollectionXML(name, prefix='', xml_node=None, owner='TBD', release='TBD'):
    collection_name = name + "Collection"

    if xml_node is None:
        collection_xml_root = add_CSDL_Headers(None)
        add_reference(
            collection_xml_root, "http://redfish.dmtf.org/schemas/v1/Resource_v1.xml", "Resource.v1_0_0", None)
        add_reference(
            collection_xml_root, "http://redfish.dmtf.org/schemas/v1/" + prefix + name + "_v1.xml", prefix + name, name.split('.')[-1])

        collection_data_services_node = SubElement(
            collection_xml_root, 'edmx:DataServices')
    else:
        collection_xml_root = xml_node
        collection_data_services_node = xml_node.find('./')


    collection_schema_node = SubElement(collection_data_services_node, 'Schema')
    collection_schema_node.set("xmlns", "http://docs.oasis-open.org/odata/ns/edm")
    collection_schema_node.set("Namespace", prefix + collection_name)

    add_annotation(collection_schema_node, {"Term": "Redfish.OwningEntity", "String": owner})

    collection_target = SubElement(collection_schema_node, "EntityType")
    collection_target.set('Name', collection_name.split('.')[-1])
    collection_target.set('BaseType', "Resource.v1_0_0.ResourceCollection")

    add_annotation(collection_target, {"Term": "OData.Description",
        "String": "A Collection of " + name + " resource instances."
        })
    add_annotation(collection_target, {"Term": "OData.LongDescription",
        "String": "A Collection of " + name + " resource instances."
        })
    add_collection_annotation(collection_target, {"Term":
        "Capabilities.InsertRestrictions"}, {"Insertable": "false"})
    add_collection_annotation(collection_target, {"Term":
        "Capabilities.UpdateRestrictions"}, {"Updatable": "false"})
    add_collection_annotation(collection_target, {"Term":
        "Capabilities.DeleteRestrictions"}, {"Deletable": "false"})

    nav_prop = SubElement(collection_target, 'NavigationProperty')
    nav_prop.set('Name', 'Members')
    listname = name.split('.')[-1]
    # should this be without the namespace at all (errata)
    nav_prop.set('Type', 'Collection(' + listname + '.' + listname + ')')
    add_annotation(nav_prop, {'Term':'OData.Permissions',
        'EnumMember':'OData.Permissions/Read'})
    add_annotation(nav_prop, {'Term':'OData.Description', 'String':'Contains members of this collection.'})
    add_annotation(nav_prop, {'Term':'OData.LongDescription', 'String':'Contains members of this collection.'})
    add_annotation(nav_prop, {'Term':'OData.AutoExpandReferences'})
    add_annotation(nav_prop, {'Term': 'Redfish.Required'})
    return collection_xml_root


def create_xml_base(csdlname, prefix='', xml_node = None, owner='TBD', release='TBD'):
    if xml_node is None:
        main_node = add_CSDL_Headers(True)
        add_reference(main_node,
                "http://redfish.dmtf.org/schemas/v1/Resource_v1.xml",
                "Resource.v1_0_0", None )
        entity_node = None
        # add refs to main, then add data services node
        data_services_node = Element('edmx:DataServices')
    else:
        main_node = xml_node
        data_services_node = xml_node.find('./')
    schema_node = SubElement(data_services_node, 'Schema')
    schema_node.set(
        'Namespace', prefix + csdlname + ".v1_0_0")
    schema_node.set(
        'xmlns', 'http://docs.oasis-open.org/odata/ns/edm')
    add_annotation(schema_node, {"Term": "Redfish.OwningEntity", "String": owner})
    add_annotation(schema_node, {"Term": "Redfish.Release", "String": release})
    # add in first schema
    schema_node_og = Element('Schema')
    schema_node_og.set('Namespace', prefix + csdlname)
    schema_node_og.set(
        'xmlns', 'http://docs.oasis-open.org/odata/ns/edm')
    add_annotation(schema_node_og, {"Term": "Redfish.OwningEntity", "String": owner})
    data_services_node.insert(0, schema_node_og)

    schema1_entity = SubElement(schema_node_og, 'EntityType')
    schema1_entity.set('Name', csdlname.split('.')[-1])
    schema1_entity.set('BaseType', 'Resource.v1_0_0.Resource')
    schema1_entity.set(
        'Abstract', 'true')
    add_annotation(schema1_entity, {
                   'Term': 'OData.Description', 'String': 'Parameters for {}.'.format(csdlname)})
    add_annotation(schema1_entity, {
                   'Term': 'OData.LongDescription', 'String': 'Parameters for {}.'.format(csdlname)})
    add_collection_annotation(schema1_entity, {"Term":
        "Capabilities.InsertRestrictions"}, {"Insertable": "false"})
    add_collection_annotation(schema1_entity, {"Term":
        "Capabilities.UpdateRestrictions"}, {"Updatable": "false"})
    add_collection_annotation(schema1_entity, {"Term":
        "Capabilities.DeleteRestrictions"}, {"Deletable": "false"})
    main_node.append(data_services_node)
    return main_node, schema_node, data_services_node