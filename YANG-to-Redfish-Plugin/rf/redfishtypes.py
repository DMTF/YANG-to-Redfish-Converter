# Copyright Notice:
# Copyright 2017 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

import string

types_mapping = {
    'binary':            'Edm.Binary',
    'bits':              'Edm.Binary',
    'boolean':           'Edm.Boolean',
    'date_and_time':     'Edm.DateTimeOffset',
    'decimal64':         'Edm.Decimal',
    'empty':             'RedfishYang.empty',  # clause
    'enumeration':       'Edm.EnumType',  # clause
    'identityref':       'RedfishYang.instance_identifier',  # clause
    'int8':              'Edm.Sbyte',
    'int16':             'Edm.Int16',
    'int32':             'Edm.Int32',
    'int64':             'Edm.Int64',
    'leafref':           'Edm.String',  # clause
    'string':            'Edm.String',
    'uint8':             'Edm.Byte',
    'uint16':            'RedfishYang.uint16',
    'uint32':            'RedfishYang.uint32',
    'uint64':            'RedfishYang.uint64',
    'union':             'Edm.Primitive',  # clause
    'anyxml':            'RedfishYang.XmlBlock',  # clause
    "counter32": 'Edm.String',
    "counter64": 'Edm.String',
    "domain_name": 'Edm.String',
    "dotted_quad": 'Edm.String',
    "gauge64": 'Edm.String'
}

enum_mapping_left = {
    'leaf':         'NodeType' # also for leaflist, module, all other Nodes
}

enum_mapping_right = {
    'leaf':         'NodeTypes', # also for leaflist, module, all other Nodes
    'yin-element':  'YinElement',
    'status':       'NodeStatus',
    'config':       'ConfigPermission',
    'mandatory':    'Mandatory'
}


def get_valid_csdl_identifier(name):
    """
    Replace characters that are invalid in CSDL with appropriate valid ones
    """
    new_name = name.replace('-', '_').replace(':', '.').replace('"', '').replace('\'', '')
    dots = new_name.split('.')
    # dots = [string.capwords(s, '_') for s in dots]

    # return '.'.join(dots).replace('_', '')
    return '.'.join(dots)

def get_annotation_enum(node_type, enum_val):
    """
    Return the CSDL mapping of the current YANG statement.
    :param node_type: YANG statment type
    :return The Redfish Node type in appropriate CSDL string format:
    """
    enum_name_left = 'RedfishYang.{}'.format(enum_mapping_left.get(node_type, get_valid_csdl_identifier(node_type)))
    enum_name_right = 'RedfishYang.{}'.format(enum_mapping_right.get(node_type, get_valid_csdl_identifier(node_type)))
    return enum_name_left, '{}/{}'.format(enum_name_right, get_valid_csdl_identifier(enum_val))

def get_descriptive_properties_mapping(property_name):
    """
    Return the CSDL property mapping of the current YANG statement.
    :param node_type: YANG statment type
    :return The Redfish Node type in appropriate CSDL string format:
    """
    target_name = get_valid_csdl_identifier(property_name)
    return 'RedfishYang.' + str(target_name)
