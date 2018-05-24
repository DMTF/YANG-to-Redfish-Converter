# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

import string

types_mapping = {
    'binary': 'Edm.Binary',
    'bits': '',
    'boolean': 'Edm.Boolean',
    'decimal64': 'Edm.Decimal',
    'empty': '',
    'enumeration': 'Edm.EnumType',
    'identityref': 'Edm.String',
    'int8': 'Edm.Sbyte',
    'int16': 'Edm.Int16',
    'int32': 'Edm.Int32',
    'int64': 'Edm.Int64',
    'leafref': 'Edm.String',
    'string': 'Edm.String',
    'uint8': 'Edm.Byte',
    'uint16': 'RedfishYang.uint16',
    'uint32': 'RedfishYang.uint32',
    'uint64': 'RedfishYang.uint64',
    'union': '',
    'date_and_time': 'Edm.DateTimeOffset'
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


def get_node_types_mapping(node_type):
    """
    Return the CSDL mapping of the current YANG statement.
    :param node_type: YANG statment type
    :return The Redfish Node type in appropriate CSDL string format:
    """
    return 'RedfishYang.NodeTypes/' + get_valid_csdl_identifier(node_type)

def get_descriptive_properties_mapping(property_name):
    """
    Return the CSDL property mapping of the current YANG statement.
    :param node_type: YANG statment type
    :return The Redfish Node type in appropriate CSDL string format:
    """
    if property_name == 'description':
        return 'OData.Description'
    target_name = get_valid_csdl_identifier(property_name) 
    return 'RedfishYang.' + str(target_name)
