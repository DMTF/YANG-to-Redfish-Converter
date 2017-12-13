# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

types_mapping = {
    'binary': 'Edm.Binary',
    'bits': '',
    'boolean': 'Edm.Boolean',
    'decimal64': 'Edm.Decimal',
    'empty': '',
    'enumeration': 'Edm:EnumType',
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
    'date-and-time': 'Edm.DateTimeOffset'
}

node_types_mapping = {
    'ContainerKeyword': 'container',
    'ListKeyword': 'list',
    'ChoiceKeyword': 'choice',
    'CaseKeyword': 'case',
    'RpcKeyword': 'rpc',
    'LeafKeyword': 'leaf',
    'LeafListKeyword': 'leaf_list',
    'Notification': 'notification'
}

def get_node_types_mapping(node_type):
    """
    Return the CSDL mapping of the current YANG statement.
    :param node_type: YANG statment type
    :return The Redfish Node type in appropriate CSDL string format:
    """
    target_type = node_types_mapping.get(node_type, 'Undefined')
    return 'RedfishYang.NodeTypes/' + target_type

property_mapping = {
    'argument': 'argument',
    'augment': 'augment',
    'base': 'base',
    'bits': 'bits',
    'Case': 'case',
    'case': 'case',
    'Contact': 'contact',
    'Choice': 'choice',
    'choice': 'choice',
    'description': 'description',
    'deviation': 'deviation',
    'deviate': 'deviate',
    'error-message': 'error_message',
    'error-app-tag': 'error_app_tag',
    'extension': 'extension',
    'Feature': 'feature',
    'IfFeature': 'if_feature',
    'isxml': 'IsXml',
    'length': 'length',
    'min': 'min',
    'min-elements': 'min_elements',
    'max': 'max',
    'max-elements': 'max_elements',
    'must': 'must',
    'Organization': 'organization',
    'ordered-by': 'ordered_by',
    'path': 'path',
    'presence': 'presence',
    'range': 'range',
    'Reference': 'reference',
    'reference': 'reference',
    'Revision': 'revision',
    'status': 'status',
    'Statement': 'statement',
    'Units': 'units',
    'unique': 'unique',
    'when': 'when',
    'When': 'when',
    'xmlblock': 'XmlBlock',
    'YangType': 'YangType',
    'YangVersion': 'yang_version',
    'YinElement': 'yin'
}


def get_descriptive_properties_mapping(property_name):
    """
    Return the CSDL property mapping of the current YANG statement.
    :param node_type: YANG statment type
    :return The Redfish Node type in appropriate CSDL string format:
    """
    if property_name == 'Description':
        return 'OData.Description'
    target_name = property_mapping.get(property_name, 'Undefined')
    return 'RedfishYang.' + str(target_name)
