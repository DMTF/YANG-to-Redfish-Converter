from xml.etree.ElementTree import Element, SubElement, tostring
from collections import namedtuple
from rf.xml_convenience import create_xml_base, createCollectionXML, createExtensionsXML, add_reference
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
    def get_full_csdlname(self):
        if self.parent is not None:
            return '.'.join([self.parent.get_full_csdlname(), self.csdlname])
        else:
            return self.csdlname
    
    def __init__(self, yang_obj, parent=None, other_docs={}):
        print('new obj')
        self.yang_obj = yang_obj
        self.keyword = self.yang_obj.keyword
        self.arg = self.yang_obj.arg
        self.arg = self.arg.replace('\n', ' ') if self.arg is not None else ''
        self.parent = parent

        self.csdlname = get_valid_csdl_identifier(self.arg)
        full_csdlname = self.get_full_csdlname()
        csdlname_type = self.csdlname.split('.')[-1]

        self.my_doc = DocNodes(*create_xml_base(full_csdlname), self.csdlname, {self.arg: self}, {})
        self.used_imports = {}

        self.external_docs = other_docs

        self.children = []

        if parent is not None:
            parent.children.append(self)
            self.external_docs = parent.external_docs
    
        self.additional_docs = []

        self.content = collectChildren(yang_obj)

        print('YangTAG--- {} {}'.format(self.keyword, self.arg))
        if self.keyword in ['module','submodule', 'container', 'list', 'grouping']:
            entity_node = Element('EntityType', {
                'Name': csdlname_type,
                'BaseType': self.get_full_csdlname() + '.' + csdlname_type
            })

            handle_generic_node('leaf', self.keyword, entity_node)

            if self.keyword in ['list']:
                collection_csdlname = self.get_full_csdlname() + 'Collection'
                self.additional_docs.append(DocNodes(createCollectionXML(full_csdlname), None, None, collection_csdlname, {}, {}))

            if self.keyword in ['module', 'container', 'list', 'submodule', 'grouping']:
                self.consume_tags(entity_node)
            
            self.my_doc.Schema.append(entity_node)
        else:
            print('Given tag is NOT convertable into a CSDL document alone')
            raise ValueError
        if len(self.my_doc.types) > 0:
            createExtensionsXML(self.csdlname, self.my_doc.types, self.my_doc.Schema)

        collectAnnotations(self.my_doc.Schema)


    def get_sub_children(self):
        children = []
        for c in self.children:
            children.extend(c.get_sub_children())
        children.extend(self.children)
        return children

    def get_import(self, name):
        if name in self.my_doc.imports:
            return self.my_doc.imports[name]
        elif self.parent is not None:
            return self.parent.get_import(name)
        else:
            return None

    def get_type(self, name):
        if name in self.my_doc.types:
            return self.my_doc.types[name]
        elif self.parent is not None:
            return self.parent.get_type(name)
        else:
            return None

    def return_docs(self, single_file=False):
        if not single_file:
            for i in self.used_imports:
                child = self.used_imports[i]
                if child == self:
                    continue
                add_reference(self.my_doc.Main, '', child.get_full_csdlname(), alias=i, version='v1_0_0')
            yield XMLContent.create_doc_with(self.get_full_csdlname(), self.my_doc.Main)
            for doc in self.additional_docs:
                add_reference(self.my_doc.Main, '', doc.prefix, version='v1_0_0')
                yield XMLContent.create_doc_with(doc.prefix, doc.Main)
            for child in self.children:
                add_reference(self.my_doc.Main, '', child.get_full_csdlname(), version='v1_0_0')
                for doc in child.return_docs(single_file):
                    yield doc 
        else:
            my_used_imports = {}
            my_used_imports.update(self.used_imports)
            for child in self.get_sub_children():
                for node in child.my_doc.DataService:
                    self.my_doc.DataService.append(node)
                my_used_imports.update(child.used_imports)
                my_used_imports = {x: my_used_imports[x] for x in my_used_imports if x not in [child.get_full_csdlname()]}
                print(my_used_imports, child.get_full_csdlname())
            for i in my_used_imports:
                child = my_used_imports[i]
                add_reference(self.my_doc.Main, '', child.get_full_csdlname(), alias=i, version='v1_0_0')
            yield XMLContent.create_doc_with(self.get_full_csdlname(), self.my_doc.Main)
            

    def consume_tags(self, node, tag_names=None):
        for tag in self.content:
            if tag_names is not None and tag.keyword not in tag_names:
                print('not in accept')
            if tag.keyword in ['import', 'include']:
                # TODO: Create proper statement from this tag
                import_name, prefix, date = tag.arg, tag.arg, None
                for item in collectChildren(tag):
                    if item.keyword == "prefix":
                        prefix = item.arg
                    if item.keyword == "revision-date":
                        date = item.arg
                if tag.arg in self.external_docs:
                    self.my_doc.imports[prefix] = self.external_docs[tag.arg]
                else:
                    print('doc not found in previous?')
            elif tag.keyword in ['prefix']:
                self.my_doc.imports[tag.arg] = self
            elif tag.keyword in ["container", "list"]:
                create_container(tag, node, self)
            elif tag.keyword in ['leaf', 'leaf-list', 'notification', 'anyxml']:
                create_leaf(tag, node, self)
            else:
                consume_tag_basic(tag, node, self)


def collectAnnotations(node):
    """
    Taking a node with possible repeated annotations, place them into their own Records
    For each discovered Term, place into new list; if list is greater than 1, create collection
    """
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
                NewAnnotation = target[0]
                NewAnnotation.attrib['String'] = NewAnnotation.attrib.get('String', '')
                for repeat in target[1:]:
                    node.remove(repeat)
                    NewAnnotation.attrib['String'] += ',  ' + repeat.attrib['String']
    for n in node:
        collectAnnotations(n)


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


def create_container(yang_obj, target, parent):
    mobj = YangCSDLConversionObj(yang_obj, parent)
    csdlname = mobj.csdlname

    if yang_obj.keyword in ['grouping']:
        return

    navigation_property = SubElement(target, 'NavigationProperty')

    # Handle Container Grammar
    if yang_obj.keyword in ['container']:
        tname = csdlname.split('.')[-1]
        parent.my_doc.imports[csdlname] = mobj
        navigation_property.set('Name', tname + 'Container')
        navigation_property.set('Type', mobj.get_full_csdlname() + '.' + tname)

    # Handle List Grammar
    if yang_obj.keyword in ['list']:
        csdlname = csdlname + 'Collection'
        tname = csdlname.split('.')[-1]
        parent.my_doc.imports[csdlname] = csdlname
        navigation_property.set('Name', tname)
        navigation_property.set('Type', mobj.get_full_csdlname() + '.' + tname)

    navigation_property.set('ContainsTarget', 'true')

    # At the end of the grammar, modify outside nav property
    xml_convenience.add_annotation(navigation_property, {'Term': 'OData.Permissions', 'EnumMember': 'OData.Permissions/Read'})
    xml_convenience.add_annotation(navigation_property, {'Term': 'OData.Description', 'String': 'Navigation property that points to a resource of {}.'.format(str(csdlname))})
    xml_convenience.add_annotation(navigation_property, {'Term': 'OData.LongDescription', 'String': 'Automatically generated.'})
    xml_convenience.add_annotation(navigation_property, {'Term': 'OData.AutoExpandReferences'})



def create_leaf(yang_obj, target, parent):
    csdlname = get_valid_csdl_identifier(yang_obj.arg)

    my_content = collectChildren(yang_obj)

    if yang_obj.keyword == 'notification':
        prop_node = SubElement(parent.my_doc.Schema, "EntityType", { 
            'Name': csdlname,
            'BaseType': 'Resource.v1_0_0.Resource'
        })
    else:
        prop_node = SubElement(target, "Property", {
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
        create_container(tag, target, parent)
    elif tag.keyword in ["container", "list"]:
        create_container(tag, target, parent)
    elif tag.keyword in ['leaf', 'leaf-list', 'notification', 'anyxml']:
        create_leaf(tag, target, parent)
    else:
        if type(tag.keyword) == tuple or ':' in tag.keyword:
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
    if yang_obj.arg:
        yang_obj.arg.replace('\n', '')
    else:
        yang_obj.arg = ''
    annotation = xml_convenience.add_annotation(
        target, {'Term': redfishtypes.get_descriptive_properties_mapping(yang_obj.keyword), 'String': yang_obj.arg.replace('\n', '')})
    
    my_children = collectChildren(yang_obj)
    if len(my_children) > 0:
        print('Skipped children {} in tag {} {}'.format(len(my_children), yang_obj.keyword, yang_obj.arg))

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

    my_children = collectChildren(yang_obj)
    if len(my_children) > 0:
        print('Skipped children {} in tag {} {}'.format(len(my_children), yang_obj.keyword, yang_obj.arg))

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

    my_children = collectChildren(yang_obj)
    if len(my_children) > 0:
        print('Skipped children {} in tag {} {}'.format(len(my_children), yang_obj.keyword, yang_obj.arg))

    return annotation


def dereference_type(tag, target, parent):
    location = 'none'
    if tag.arg in redfishtypes.types_mapping:
        return 'RedfishYang', redfishtypes.types_mapping[tag.arg], tag.arg
    if ':' not in tag.arg:
        print('colon seperator not in type')
        location, yang_type = parent.arg, tag.arg
    else:
        location, yang_type = tuple(tag.arg.split(':'))
    target_doc = parent.get_import(location)
    if target_doc is None:
        print('type location not found')
        return location, None, None
    elif yang_type not in target_doc.my_doc.types:
        # manage circular imports here, just put new type def for now
        my_type = target_doc.get_type(yang_type)
        if my_type is not None:
            target_doc.my_doc.types[yang_type] = my_type
            target_doc.my_doc.Schema.append(my_type)
        else:
            print('type not found in location document')
            return location, None, None
        location = target_doc.get_full_csdlname() + '.v1_0_0'
        return location, target_doc.get_full_csdlname() + '.v1_0_0.' + get_valid_csdl_identifier(yang_type), yang_type
    else:
        location = target_doc.get_full_csdlname() + '.v1_0_0'
        parent.used_imports[target_doc.get_full_csdlname()] = target_doc
        return location, target_doc.get_full_csdlname() + '.v1_0_0.' + get_valid_csdl_identifier(yang_type), yang_type


def handle_type(tag, target, parent):
    """ 
    Handle a 'type' tag
    tag: pyang object for type enumeration
    target: xml tag to place resulting node
    parent: parent YangCSDLConversionObj for document access
    """
    yang_type_location, yang_type = "RedfishYang", tag.arg
    if tag.arg in redfishtypes.types_mapping:
        my_type = redfishtypes.types_mapping[tag.arg]
    else:
        yang_type_location, my_type, yang_type = dereference_type(tag, target, parent)
        if my_type is None:
            yang_type_location = "RedfishYang"
            my_type = redfishtypes.types_mapping['string']
            yang_type = 'string'

    annotation = SubElement(target, 'Annotation', {
        'Term': yang_type_location + '.YangType',
        'EnumMember': yang_type_location + '.YangTypes/' + yang_type
    })

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
                yang_type = 'enumeration'
            else:
                yang_type_location, my_type, yang_type = dereference_type(inner_tag, target, parent)
                if yang_type is None:
                    yang_type_location, yang_type = 'RedfishYang', 'string' 
                    new_node.set('UnderlyingType', 'Edm.String')
                else:
                    new_node.set('UnderlyingType', my_type)
                annotation = SubElement(new_node, 'Annotation', {
                    'Term': yang_type_location + '.YangType',
                    'EnumMember': yang_type_location + '.YangTypes/' + yang_type
                })
        else:
            consume_tag_basic(inner_tag, new_node, parent)

    if yang_type != 'enumeration':
        parent.my_doc.types[tag.arg] = new_node


def handle_enumeration(tag, target, name, parent):
    """
    Handle a 'type enumeration' tag
    tag: pyang object for type enumeration
    target: xml tag to place resulting node
    parent: parent YangCSDLConversionObj for document access
    """

    prop_node = SubElement(target, 'EnumType', {
        'Name': name + 'Enumeration'
    })

    parent.my_doc.types[name+'Enumeration'] = prop_node

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
            

