# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

"""

Redfish output plugin

Based on 'name', 'tree' plugin

"""

import optparse
import os
from xml.etree.ElementTree import tostring
import rf.yangobj as yangobj
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
            optparse.make_option("--target_dir",
                                 dest="target_dir",
                                 help="Where to output xml files"),
            optparse.make_option("--create_groupings",
                                 dest="create_groupings",
                                 action="store_true",
                                 help="Create XML definitions for grouping definitions pulled by uses"),
            optparse.make_option("--keep_cyclical_imports",
                                 dest="keep_cyclical_imports",
                                 action="store_true",
                                 help="Keep possible cyclical imports to module xml"),
            optparse.make_option("--combine_all_nodes",
                                 dest="combine_all_nodes",
                                 action="store_true",
                                 help="Combine all XML files to a single file"),
            optparse.make_option("--release",
                                 dest="release",
                                 help="Release version of files (default TBD)"),
            optparse.make_option("--owning_entity",
                                 dest="owning_entity",
                                 help="Owning entity of files (default TBD)"),
            ]
        g = optparser.add_option_group("Redfish output specific options")
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

        target_dir = ctx.opts.target_dir if ctx.opts.target_dir is not None else './output_dir'

        if ctx.opts.keep_cyclical_imports:
            yangobj.config['remove_cyclical'] = False

        if ctx.opts.combine_all_nodes:
            yangobj.config['single_file'] = True

        if ctx.opts.create_groupings:
            yangobj.config['no_groupings'] = False

        if ctx.opts.release:
            yangobj.config['release'] = ctx.opts.release

        if ctx.opts.owning_entity:
            yangobj.config['owner'] = ctx.opts.owning_entity

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        list_of_xml = []
        other_docs = {}
        import_counts = {}
        my_modules = {}

        for module in modules:
            my_modules[module.arg] = module
            import_counts[module.arg] = set([tag.arg for tag in yangobj.collectChildren(module) if tag.keyword in ['import']])
        
        satisfied_modules = [my_modules[x] for x in my_modules if len(import_counts[x]) == 0]
        unsatisfied_modules = {x: my_modules[x] for x in my_modules if len(import_counts[x]) > 0}

        finished_modules = set()

        while len( satisfied_modules ) > 0:
            for module in satisfied_modules:
                print(module.arg)
                mobj = yangobj.YangCSDLConversionObj(module, other_docs=other_docs)
                other_docs.update(mobj.my_doc.imports)
                list_of_xml.extend(mobj.return_docs(yangobj.config['single_file']))
            done = set(other_docs.keys())
            satisfied_modules = [unsatisfied_modules[x] for x in unsatisfied_modules if len(import_counts[x].difference(done)) == 0]
            unsatisfied_modules = {x: unsatisfied_modules[x] for x in unsatisfied_modules if len(import_counts[x].difference(done)) > 0}

        done = set(other_docs.keys())
        if len(unsatisfied_modules) > 0:
            for x in unsatisfied_modules:
                module = unsatisfied_modules[x]
                mobj = yangobj.YangCSDLConversionObj(module, other_docs=other_docs)
                other_docs.update(mobj.my_doc.imports)
                list_of_xml.extend(mobj.return_docs(yangobj.config['single_file']))



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

                tokened_line = tokened_line.replace('&quot;', '"')
                pretty_xml_as_string_new += tokened_line + '\n'

            try:
                write_to_file(filename, pretty_xml_as_string_new)
                print('Success writing file to disk: ' + filename)
                logger.info('Success writing file to disk: ' + filename)
            except BaseException as e:
                print('Unable to write to file: ' +
                      filename + "\nError message: " + str(e))
                logger.error('Unable to write to file: ' +
                             filename + "\nError message: " + str(e))

        if len(unsatisfied_modules) > 0:
            print('There were unsatisfied modules: ')
            for x in unsatisfied_modules:
                print('{} required: {}'.format(x, list(import_counts[x].difference(done))))


def write_to_file(filename, xml_string):
    output_file = open(filename, 'w')
    xml_string.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>')
    output_file.write(xml_string)
    output_file.close()
