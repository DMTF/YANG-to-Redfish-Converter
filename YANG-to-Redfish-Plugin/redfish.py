# Place copyright here
"""

Redfish output plugin

Based on 'name', 'tree' plugin

"""

import optparse
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, dump
import rf.csdltree as csdltree
import logging
import xml.dom.minidom
import re

from pyang import plugin


def pyang_plugin_init():
    plugin.register_plugin(RedfishPlugin())


class RedfishPlugin(plugin.PyangPlugin):
    def add_output_format(self, fmts):
        self.multiple_modules = True
        fmts['redfish'] = self

    def add_opts(self, optparser):
        optlist = [
            optparse.make_option("--example",
                                 dest="example",
                                 action="store_true",
                                 help="Print the name and revision in name@revision format"),
            ]
        g = optparser.add_option_group("Name output specific options")
        g.add_options(optlist)

    def setup_ctx(self, ctx):
        pass

    def setup_fmt(self, ctx):
        ctx.implicit_errors = False

    def emit(self, ctx, modules, fd):
        logger = logging.getLogger('yang_to_csdl')
        hdlr = logging.FileHandler('yang_to_csdl.log', mode='w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.DEBUG)

        list_of_xml = []
        target_dir = '.'

        csdltree.setLogger(logger)

        path = None
        if ctx.opts.tree_path is not None:
            path = ctx.opts.tree_path.split('/')
            if path[0] == '':
                path = path[1:]
            csdltree.path = path

        for module in modules:
            xml_root = csdltree.build_tree(module, list_of_xml, logger)
            break

        for xml_item in list_of_xml:
            filename = target_dir + '/' + xml_item.get_filename()
            xml_string = tostring(xml_item.get_xml(), encoding="unicode", method="xml")
            xml_obj = xml.dom.minidom.parseString(xml_string)
            pretty_xml_as_string = xml_obj.toprettyxml()
            pretty_xml_as_string_new = ''

            # input(pretty_xml_as_string)
            # post process Annotations
            priority_tags = ["xmlns", "xmlns:edmx", "Name", "Term", "Property", "Type", "Namespace", "EnumMember", "String", "Bool"]
            for line in pretty_xml_as_string.split('\n'):
                priority_tag_dict = {}
                other_tags = []
                allresults = re.findall('[a-zA-Z:]+?=".+?"', line)
                tokened_line = re.sub('[a-zA-Z:]+?=".+?"', 'xxToken', line)
                for tag in allresults:
                    tag_name, tag_content = tuple(tag.split('=', 1))
                    if tag_name not in priority_tags:
                        other_tags.append(tag_name)
                    priority_tag_dict[tag_name] = tag

                for tag_name in priority_tags + other_tags:
                    if tag_name in priority_tag_dict:
                        tokened_line = tokened_line.replace('xxToken', priority_tag_dict[tag_name], 1)

                pretty_xml_as_string_new += tokened_line + '\n'

            try:
                write_to_file(filename, pretty_xml_as_string_new)
                logger.info('Success writing file to disk: ' + filename)
            except BaseException as e:
                logger.error('Unable to write to file: ' +
                             filename + "\nError message: " + str(e))

def write_to_file(filename, xml_string):
    output_file = open(filename, 'w')
    xml_string.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>')
    output_file.write(xml_string)
    output_file.close()

