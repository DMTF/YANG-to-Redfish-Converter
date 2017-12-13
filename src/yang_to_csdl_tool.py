#!/usr/bin/python
# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/LICENSE.md

from yang.module import ModuleGrammar
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, dump
from redfishtypes import types_mapping
from csdltree import build_tree_new
from libs.fileops import write_to_file
import argparse
import sys
import logging
import os
import xml.dom.minidom
import re

grammar_whitespace_mode = 'optional'

# Dict of mappings from string to log levels
log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


#=======================================================================
def print_version():
    version = 'Version 1.0'
    print('YANG to CSDL Converter version: {0} '.format(version))

#=======================================================================


def execute(filename, output_grammar, target_dir, logger):
    """
    Setup all the files, directories, variables required for the convertor to
    work and invoke the convetor.
    :param filename: YANG model source
    :param target_dir: Directory where CSDL XML files will be stored
    :param logger: Logger object
    """
    myparser = ModuleGrammar.parser()
# Read the entire file into a string and parse.
    with open(filename) as content_file:
        content = content_file.read()
# Before we parse yang, let's strip out all the comments!
    content = re.sub("(\/\/)[^\n\r]*[\n\r]", "", content)
    # https://stackoverflow.com/questions/462843/improving-fixing-a-regex-for-c-style-block-comments 
    content = re.sub("\/\*((?=)((?=)((?=)[^*]+)|\*(?!\/))*)\*\/", "", content)
    
# Parse the YANG
    result = myparser.parse_text(content)
    try:
        os.mkdir(target_dir)
    except OSError:
        logger.error(
            'Unable to create target directory {0}'.format(target_dir))
        logger.error('Directory may already exist')

# Build the tree
    list_of_xml = list()
    xml_root = build_tree_new(result, list_of_xml, logger)

    if output_grammar:
        sys.stdout.writelines(generate_ebnf(ModuleGrammar))
    for xmls in list_of_xml:
        filename = target_dir + '/' + xmls.get_filename()
        xml_string = tostring(xmls.get_xml(), encoding="unicode", method="xml")
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
                tag_name, tag_content = tuple(tag.split('='))
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



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input', help='Path of the input YANG model file.', dest='input_file')
    parser.add_argument('--output-grammar',  help='Output the grammar used to translate from YANG to CSDL',
                        dest='output_grammar', action='store_true')
    parser.add_argument('--verbose',  help='Verbose output',
                        dest='verbose', default='debug')
    parser.add_argument('--output-dir', default='.', help='Full path of\
            destination where xml files must be stored; \
            defaults to current directory. Filenames are extracted from the \
            YANG module/container/list definitions. Files will be overwritten\
            without warning.', dest='target_dir')
    parser.add_argument('--version', help='Display version information and exit.',
                        action='store_true', dest='version')
    args = parser.parse_args()
    return args
#=======================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ('Insufficient commandline arguments. Please run with -h to view \
options')
        sys.exit()

    args = parse_args()
    if args.version is True:
        print_version()
        sys.exit()
    filename = os.path.abspath(args.input_file)
    if filename is None:
        print('No input file specified.')
        logger.info('No input file specified')
        sys.exit()
    if not os.path.isfile(filename):
        print('Input path is not a regular file.')
        sys.exit()

    logger = logging.getLogger('yang_to_csdl')
    hdlr = logging.FileHandler('yang_to_csdl.log', mode='w')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(log_levels.get(args.verbose.upper()))

    if args.target_dir == '.' or args.target_dir is None:
        args.target_dir = args.input_file.replace('.', '_').rsplit('/')[-1]
        print('No output directory specified. Writing to directory {}.'.format(args.target_dir))
        logger.info(
            'No output directory specified. Writing to directory {}.'.format(args.target_dir)
        )
    execute(filename, args.output_grammar, args.target_dir, logger)
