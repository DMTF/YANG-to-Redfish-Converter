from xml.etree.ElementTree import Element, SubElement, tostring
from collections import namedtuple
from rf.xml_convenience import create_xml_base, createCollectionXML
from rf.redfishtypes import get_valid_csdl_identifier
from rf.xml_content import XMLContent
import rf.redfishtypes as redfishtypes
import rf.xml_convenience as xml_convenience

DocNodes = namedtuple('DocNodes', ['Main', 'Schema', 'DataService', 'prefix', 'imports', 'types'])

config = {
        'single_file': False,
        'no_groupings': True,
        'remove_cyclical': True,
        'owner': 'TBD',
        'release': 'TBD',
        'debug': True
        }

terminate = False

class YangCSDLConversionObj:
    def __init__(self, yang_obj, parent=None):
        print('new obj')
        self.yang_obj = yang_obj
        self.keyword = self.yang_obj.keyword
        self.arg = self.yang_obj.arg
        self.arg = self.arg.replace('\n', ' ') if self.arg is not None else ''
        self.parent = parent

        self.csdlname = get_valid_csdl_identifier(self.arg)
        if parent is not None:
            self.csdlname = '.'.join([parent.csdlname, self.csdlname])
        csdlname = self.csdlname
        csdlname_type = csdlname.split('.')[-1]

        self.my_doc = DocNodes(*create_xml_base(csdlname), csdlname, {}, {})
        self.my_docs = { csdlname: self.my_doc }

        self.content = collectChildren(yang_obj)

        top_parent = self.parent
        if top_parent is not None:
            while top_parent.parent is not None:
                top_parent = top_parent.parent
            top_parent.my_docs.update(self.my_docs)

        print('YangTAG--- {} {}'.format(self.keyword, self.arg))
        if self.keyword in ['module','submodule', 'container', 'list', 'grouping']:
            entity_node = Element('Entity', {
                'Name': csdlname_type,
                'BaseType': '.'.join(['prefix', csdlname_type, csdlname_type])
            })

            handle_generic_node('leaf', self.keyword, entity_node)

            if self.keyword in ['list']:
                collection_csdlname = csdlname + 'Collection'
                self.my_docs[collection_csdlname] = DocNodes(createCollectionXML(csdlname), None, None, collection_csdlname, {}, {})
                top_parent.my_docs.update(self.my_docs)

            if self.keyword in ['module', 'container', 'list']:
                self.consume_tags()
        else:
            print('Given tag is NOT convertable into a CSDL document alone')
            raise ValueError
        print('leaving obj', self.my_doc.imports, self.my_doc.types)

    def return_docs(self, single_file=False):
        csdlname = get_valid_csdl_identifier(self.arg)
        if single_file:
            xml_content = XMLContent()
            xml_content.set_filename(csdlname + '_v1.xml')
            xml_content.set_xml(self.my_doc.Main)
            yield xml_content
        else:
            for doc_name, my_doc in self.my_docs.items():
                xml_content = XMLContent()
                xml_content.set_filename(doc_name + '_v1.xml')
                xml_content.set_xml(my_doc.Main)
                yield xml_content

    def consume_tags(self, tag_names=None):
        for tag in self.content:
            if tag_names is not None and tag.keyword not in tag_names:
                print('not in accept')
            if tag.keyword in ['import', 'include']:
                # TODO: Create proper statement from this tag
                import_name, prefix, date = self.arg, None, None
                for item in collectChildren(tag):
                    if item.keyword == "prefix":
                        prefix = item.arg
                    if item.keyword == "revision-date":
                        date = item.arg
            elif tag.keyword in ["container", "list"]:
                create_container(tag, self)
            elif tag.keyword in ['leaf', 'leaf-list', 'notification', 'anyxml']:
                create_leaf(tag, self)
            else:
                consume_tag_basic(tag, self.my_doc.Schema, self)


    def renderTree(self, parent_doc=None, target=None):
         


        # elif yang_keyword in ['rpc']:
        #    annotation = handle_rpc(yang_keyword, yang_arg, yang_children, target, target_entity, target_parent, list_of_xml, toplevelimports, topleveltypes, prefix)

        if self.keyword in redfishtypes.enum_mapping_right:
            annotation = handle_generic_node(self.keyword, self.arg, target)
            return parent_doc, annotation

        else:
            if self.keyword in ['uses', 'grouping', 'augment', 'include', 'import', 'belongsto', 'extension', 'prefix']:
                print('Tag ignored {}'.format(self.keyword))
                self.content = []
            elif self.keyword in ['case', 'rpc', 'choice', 'action']:
                print('Tag being defaulted {}'.format(self.keyword))
                handle_generic(self)
            else:
                annotations = handle_generic(self)
                for a in annotations:
                    target.append(a)
                if len(annotations) <= 0:
                    return parent_doc, None
                else:
                    return parent_doc, annotations[0]
        return None, None


def collectAnnotations(node):
    """
    Taking a node with possible repeated annotations, place them into their own Records
    For each discovered Term, place into new list; if list is greater than 1, create collection
    """
    return

    allAnnotations = node.findall('Annotation')

    collected = {}
    for a in allAnnotations:
        term = a.attrib.get('Term')
        if term not in collected:
            collected[term] = []
        collected[term].append(a)

    for key in collected:
        target = collected[key]
        if len(target) > 1:
            if (key == 'OData.LongDescription' or key == 'OData.Description'):
                Collection = SubElement(node, 'Annotation', attrib={'Term': key})
                text = []
                for a in target:
                    text.append(a.attrib.get('String'))
                    node.remove(a)
                Collection.attrib['String'] = '  '.join(text)
            else:
                # comment out Collection and Record lines to fix npm test
                NewAnnotation = SubElement(node, 'Annotation')
                Collection = SubElement(NewAnnotation, 'Collection')
                for repeat in target:
                    Record = SubElement(Collection, 'Record')
                    Record.append(repeat)
                    node.remove(repeat)
                    for inner_tag in repeat:
                        key = inner_tag.attrib['Term']
                        if not (key == 'OData.LongDescription' or key == 'OData.Description'):
                            inner_tag.tag = "Annotation"
                            # inner_tag.attrib['Term'] = inner_tag.attrib['Term'].split('.')[-1]


def collectChildren(yang_item):
    """
    Use pyang's child structures to determine inner tags (not entirely sure on structures)
    If i_children exists, it is likely augmented/modified, include all tags that aren't repeated
        between i_children and substmts
    Else, just use substmts
    """
    if hasattr(yang_item, 'i_children'):
        content = yang_item.i_children if len(yang_item.i_children) > 0 else []
        # print(yang_keyword, [tag.keyword for tag in content if tag not in yang_item.substmts])
        content = yang_item.substmts + [tag for tag in content if tag not in yang_item.substmts]
    else:
        # print(yang_keyword, 'HAS NO ICHILD')
        content = yang_item.substmts
    return content


def handle_description(yang_obj, target):
    yang_obj.arg = yang_obj.arg + '.' if yang_obj.arg[-1] != '.' else yang_obj.arg
    yang_obj.arg = yang_obj.arg.replace('\n', ' ')
    annotation = xml_convenience.add_annotation(
        target, {
            'Term': 'OData.Description',
            'String': yang_obj.arg.split('. ')[0].strip('.') + '.'
            }
        )
    annotation_b = xml_convenience.add_annotation(
        target, {
            'Term': 'OData.LongDescription',
            'String': yang_obj.arg
            }
        )
    return annotation_b


def create_container(yang_obj, parent):
    mobj = YangCSDLConversionObj(yang_obj, parent)
    csdlname = mobj.csdlname

    navigation_property = SubElement(parent.my_doc.Schema, 'NavigationProperty')

    # Handle Container Grammar
    if yang_obj.keyword in ['container']:
        tname = csdlname.split('.')[-1]
        parent.my_doc.imports[csdlname] = csdlname
        navigation_property.set('Name', tname + 'Container')
        navigation_property.set('Type', tname + '.' + tname)

    # Handle List Grammar
    if yang_obj.keyword in ['list']:
        csdlname = csdlname + 'Collection'
        parent.my_doc.imports[csdlname] = csdlname
        tname = csdlname.split('.')[-1]
        navigation_property.set('Name', tname)
        navigation_property.set('Type', tname + '.' + tname)

    navigation_property.set('ContainsTarget', 'true')

    # At the end of the grammar, modify outside nav property
    xml_convenience.add_annotation(navigation_property, {'Term': 'OData.Permissions', 'EnumMember': 'OData.Permissions/Read'})
    xml_convenience.add_annotation(navigation_property, {'Term': 'OData.Description', 'String': 'Navigation property that points to a resource of {}.'.format(str(csdlname))})
    xml_convenience.add_annotation(navigation_property, {'Term': 'OData.LongDescription', 'String': 'Automatically generated.'})
    xml_convenience.add_annotation(navigation_property, {'Term': 'OData.AutoExpandReferences'})



def create_leaf(yang_obj, parent):
    csdlname = get_valid_csdl_identifier(yang_obj.arg)

    my_content = collectChildren(yang_obj)

    if yang_obj.keyword == 'notification':
        prop_node = SubElement(parent.my_doc.Schema, "EntityType", { 
            'Name': csdlname,
            'BaseType': 'Resource.v1_0_0.Resource'
        })
    else:
        prop_node = SubElement(parent.my_doc.Schema, "Property", {
            'Name': csdlname,
            'Type': 'Edm.Primitive'
        })

    if yang_obj.keyword == 'leaf':
        if len([x for x in my_content if x.keyword == 'type']) == 0:
            print('leaf must include type')

    if yang_obj.keyword == 'leaf-list':
        prop_node.set(
            'Type', 'Collection({}.{})'.format('prefix' + "v1_0_0", csdlname))
        xml_convenience.add_annotation(prop_node, {"Term": "OData.LongDescription",
                "String": "List of the type {}.".format(csdlname)})

    if yang_obj.keyword == 'anyxml':
        prop_node.set('Type', redfishtypes.types_mapping[yang_obj.keyword] )

    for tag in my_content:
        consume_tag_basic(tag, prop_node, parent)

    handle_generic_node('leaf', yang_obj.keyword, prop_node)
    xml_convenience.add_annotation(
        prop_node, {'Term': 'OData.Permissions', 'EnumMember': 'OData.Permission/Read'})


def consume_tag_basic(tag, target, parent):
    if tag.keyword == "type":
        handle_type(tag, target, parent)
    elif tag.keyword in ['typedef']:
        handle_typedef(tag, target, parent)
    elif tag.keyword in ['choice']:
        handle_choice(tag, target, parent)
    elif tag.keyword == "grouping" and not config["no_groupings"]:
        create_container(tag, parent)
    elif tag.keyword in ["container", "list"]:
        create_container(tag, parent)
    elif tag.keyword in ['leaf', 'leaf-list', 'notification', 'anyxml']:
        create_leaf(tag, parent)
    else:
        if type(tag.keyword) == tuple:
            print("We don't recognize keyword {}, create as statement".format(tag.keyword))
            handle_generic_statement(tag, target)
        elif tag.keyword in ["namespace", "value", "default"]:
            handle_generic_modifier(tag, target)
        elif tag.keyword in redfishtypes.enum_mapping_right:
            handle_generic_node(tag.keyword, tag.arg, target)
        elif tag.keyword == 'description':
            handle_description(tag, target)
        else:
            handle_generic(tag, target)


def handle_generic(yang_obj, target=None):
    """
    Attempts to handle generically tags that require no special treatment
    Creates standard RedfishYang annotation, unless otherwise is "unknown" or "Description"
    """
    annotation = xml_convenience.add_annotation(
        target, {'Term': redfishtypes.get_descriptive_properties_mapping(yang_obj.keyword), 'String': yang_obj.arg.replace('\n', '')})

    return annotation


def handle_generic_statement(yang_obj, target):
    """
    Create a statement, just the most generic interpretation of a keyword
        (For unrecognized keywords or raw conversion)
    """
    if type(yang_obj.keyword) is tuple:
        yang_obj.keyword = ':'.join(yang_obj.keyword)

    string = yang_obj.keyword
    string += ' ' + yang_obj.arg if yang_obj.arg not in ['', ' ', None] else ''
    annotation = xml_convenience.add_annotation(
        target, {'Term': 'RedfishYang.statement', 'String': yang_obj.keyword})
    return annotation


def handle_generic_node (keyword, arg, target):
    """
    Handler for any Enum annotations defined in YangExtensions
    Usually of keywords with limited values, such as Deviate and Config
    """
    term, enummember = redfishtypes.get_annotation_enum(keyword, arg)
    annotation = xml_convenience.add_annotation(target, {'Term': term, 'EnumMember': enummember})
    return annotation


def handle_generic_modifier(yang_obj, target):
    """
    Handler for keywords that change attributes of a node
    as specified in the conversion spec
    """
    convert_to_csdl = {
            "namespace": "xmlns",
            "default": "DefaultValue"
            }

    annotation = handle_generic(yang_obj, target)
    if yang_obj.keyword not in ["namespace"]:
        yang_obj.keyword = convert_to_csdl.get(yang_obj.keyword, yang_obj.keyword.capitalize())
        if yang_obj.keyword != "DefaultValue":
            target.set(yang_obj.keyword, get_valid_csdl_identifier(yang_obj.arg))
    return annotation


def handle_type(tag, target, parent):
    """ 
    Handle a 'type' tag
    tag: pyang object for type enumeration
    target: xml tag to place resulting node
    parent: parent YangCSDLConversionObj for document access
    """

    yang_type_location = "RedfishYang"
    yang_type = get_valid_csdl_identifier(tag.arg.split(':')[-1])
    annotation = SubElement(target, 'Annotation', {
        'Term': 'RedfishYang.YangType',
        'EnumMember': yang_type_location + '.YangTypes/' + yang_type
    })
    if tag.arg in redfishtypes.types_mapping:
        my_type = redfishtypes.types_mapping[tag.arg]
    else:
        my_type = 'RedfishYang.' + tag.arg
    target.set('Type', my_type)
    if tag.arg == 'enumeration':
        handle_enumeration(tag, parent.my_doc.Schema, target.get('Name'), parent)
        new_enum_type = target.get('Name') + 'Enumeration'
        target.set('Type', '.'.join([parent.my_doc.Schema.get('Namespace'), new_enum_type]))
    else:
        return


def handle_typedef (tag, target, parent):
    new_node = SubElement(parent.my_doc.Schema, 'TypeDefinition', {
        'Name': get_valid_csdl_identifier(tag.arg)
    })

    parent.my_doc.types[tag.arg] = new_node

    yang_type = 'empty'
    for inner_tag in collectChildren(tag):
        if inner_tag.keyword == 'type':
            yang_type = inner_tag.arg
            yang_children_inner = collectChildren(inner_tag)
            if inner_tag.arg == 'union':
                union_annotation = xml_convenience.add_annotation(
                        new_node, {'Term': 'RedfishYang.union'})
                col = SubElement(union_annotation, 'Collection')
                for child in yang_children_inner:
                    if child.keyword != 'type':
                        continue
                    else:
                        inn = SubElement(col, 'String')
                        inn.text = '"{}"'.format(redfishtypes.get_valid_csdl_identifier(child.arg))
            elif inner_tag.arg == 'enumeration':
                parent.my_doc.Schema.remove(new_node)
                handle_enumeration(inner_tag, parent.my_doc.Schema, tag.arg, parent)
        else:
            consume_tag_basic(inner_tag, new_node, parent)

    # default to primitive instead of string, UnderlyingType must be dereferenced
    if 'Type' not in new_node.attrib:
        new_node.set('UnderlyingType', redfishtypes.types_mapping.get(yang_type, 'Edm.Primitive'))
    else:
        new_node.set('UnderlyingType', new_node.attrib.pop('Type'))


def handle_enumeration(tag, target, name, parent):
    """
    Handle a 'type enumeration' tag
    tag: pyang object for type enumeration
    target: xml tag to place resulting node
    parent: parent YangCSDLConversionObj for document access
    """

    prop_node = SubElement(target, 'EnumType', {
        'Name': name
    })

    parent.my_doc.types[name] = "Edm.String"

    my_content = collectChildren(tag)
    for tag in my_content:
        if tag.keyword == 'enum':
            member_node = SubElement(prop_node, 'Member')
            member_node.set('Name', tag.arg)

            xml_convenience.add_annotation(
                    member_node, {
                            'Term': redfishtypes.get_descriptive_properties_mapping(tag.keyword),
                            'String':  tag.arg
                            }
                    )
            for tag in collectChildren(tag):
                consume_tag_basic(tag, member_node, parent)
        else:
            consume_tag_basic(tag, prop_node, parent)


def handle_choice(tag, target, parent):
    """
    Handle choice.  Single case statements automatically handled by pyang, so simply discard all other information
    """
    print('Choice is unsupported by Redfish CSDL, combining all cases into one.')
    handle_generic(tag, target)
    for case in collectChildren(tag):
        if case.keyword == 'case':
            for case_item in collectChildren(case):
                consume_tag_basic(case_item, target, parent)
            

