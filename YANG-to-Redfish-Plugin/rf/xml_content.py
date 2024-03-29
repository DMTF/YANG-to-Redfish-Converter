# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/main/LICENSE.md

grammar_whitespace_mode = 'optional'
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, dump

class XMLContent:
    filename = None
    xml_tree = None

    def __init__(self):
        pass

    @classmethod
    def create_doc_with(cls, name, node):
        xml_content = XMLContent()
        xml_content.set_filename(name + '_v1.xml')
        xml_content.set_xml(node)
        return xml_content

    def set_filename(self, filename):
        self.filename = filename

    def set_xml(self, xml):
        self.xml_tree = xml

    def get_filename(self):
        return self.filename

    def get_xml(self):
        return self.xml_tree
