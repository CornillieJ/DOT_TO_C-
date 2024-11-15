import os
import sys

if len(sys.argv) > 1:
    FILE_PATH = sys.argv[1]
else:
    FILE_PATH = 'dot.dot'

OUTPUT_FOLDER = f"output/{FILE_PATH.replace('.dot','').split('\\')[-1]}/"
ERROR_FILE = 'error.txt'
IGNORE_LIST = ['digraph','fontname','fontsize','rankdir','node', 'edge']
PRIMITIVE_TYPES = ['string','int','double','decimal','float','bool','long','void']
NON_NULLABLE_TYPES = ['int','double','decimal','float','bool','long','void', 'datetime']
KNOWN_INTERFACES = ['ienumerable','icountable','icollection']
def import_interfaces():
    if os.path.exists('interfaces_import.txt'):
        file = open('interfaces_import.txt','r')
        content = file.read()
        for interface in content.splitlines():
            if interface.strip() not in KNOWN_INTERFACES:
                KNOWN_INTERFACES.append(interface.strip())
def read_uml(file_path):
    file = open(file_path, 'r')
    content = file.read()
    return content

def is_line_relevant(line):
    for word in IGNORE_LIST:
        if line.find(word) >= 0 or len(line.strip()) == 0:
            return False
    return True

def get_relevant_lines(split_lines):
    relevant_lines = []
    for line in split_lines:
        if is_line_relevant(line):
            relevant_lines.append(line.replace('<br/>','\n').replace('<br />','\n'))
    return relevant_lines

def get_section():
    uml_content = read_uml(FILE_PATH)
    uml_split_lines = uml_content.splitlines()
    uml_relevant_lines = get_relevant_lines(uml_split_lines)
    sections = []
    current_section = ''
    for line in uml_relevant_lines:
        current_section += line + '\n'
        if line.strip()[-1] == ']':
            sections.append(current_section)
            current_section = ''
    return sections

def get_string_between(text, start, end):
    start_index = text.find(start)
    end_index = text.find(end)
    if start_index < 0 or end_index < 0: return ''
    return text[start_index+len(start):end_index]

def get_texts(class_segments):
    prop_names = []
    prop_types = []
    prop_get = []
    prop_set = []
    prop_set_accessors = []
    prop_get_accessors = []
    methods_included = []
    methods_texts=[]
    is_interface = False
    is_enum = False
    current_class_name = ''
    for i,segment in enumerate(class_segments):
        segment = segment.replace('&lt;','<').replace('&gt;','>')
        if i == 0: 
            current_class_name = get_string_between(segment,'<b>','</b>').replace('&lt;','').replace('&gt;','')
            if current_class_name == '': current_class_name =  get_string_between(segment,'<B>','</B>').replace('&lt;','').replace('&gt;','')
            current_class_type = get_class_type(current_class_name)
            current_class_name = normalize_class_name(current_class_name, current_class_type) 
            if 'interface' in current_class_type:
                is_interface = True
            if 'enum' in current_class_type:
                is_enum = True
            continue
        if i == 1 and is_interface == False:
            properties = segment.splitlines()
            for prop in properties:
                if not prop.strip(): continue
                prop = prop.replace(' ', '')
                if is_enum:
                    value = prop.replace('br','').strip('<\\/>').strip()
                    prop_names.append(value)
                    prop_types.append('enum')
                    prop_set.append(False)
                    prop_get.append(False)
                    prop_set_accessors.append('')
                    prop_get_accessors.append('')
                else:
                    prop_names.append(get_string_between(prop, '-', ':'))
                    prop_types.append(prop[prop.find(':') + 1:])
                    prop_set.append(False)
                    prop_set_accessors.append('')
                    prop_get_accessors.append('')
                    prop_get.append(False)
        else:
            if is_enum:
                is_enum = False
                continue
            methods = segment.splitlines()
            if is_interface == True:
                is_interface = False
            for m,method in enumerate(methods):
                methods_included.append(False)
                if method.strip().strip('\n') == '': continue
                methods_included[m] = True
                for j,prop_name in enumerate(prop_names):
                    method = method.replace('&lt;','<').replace('&gt;','>')
                    if method.lower().find('get' + prop_name.lower() + '(')>= 0:
                        methods_included[m] = False
                        prop_get[j] = True
                        prop_get_accessors[j] = get_accessor(method)
                    if method.lower().find('set' + prop_name.lower() + '(')>= 0:
                        methods_included[m] = False
                        prop_set[j] = True
                        prop_set_accessors[j] = get_accessor(method)
                if methods_included[m]:
                    (method_text,constructor_assignments) = build_method_text(method,current_class_name,prop_types, prop_names)
                    methods_texts.append(method_text.replace('datetime', 'DateTime'))
                    methods_texts.append('{')
                    for assignment in constructor_assignments:
                        methods_texts.append(assignment)
                    methods_texts.append('}')

    property_texts = build_properties(prop_names, prop_types, prop_get, prop_set, prop_get_accessors, prop_set_accessors)
    fields = []
    for prop_text in property_texts:
        if '_' in prop_text:
            fields.append(prop_text[prop_text.find('_')+1: prop_text.find(';')])
    for i, method in enumerate(methods_texts):
        for field in fields:
            if f'{field.capitalize()} =' in method:
                methods_texts[i] = method.replace(field.capitalize(),f'_{field}')

    return property_texts, methods_texts

def build_properties(prop_names, prop_types, prop_get, prop_set, get_accessors, set_accessors):
    property_texts = []
    for i, prop_name in enumerate(prop_names):
        current_prop = []
        if prop_name == '' or prop_types[i] == '': 
            continue
        prop_types[i] = capitalize_type_correctly(prop_types[i])
        if prop_types[i].lower() == 'enum':
            current_prop = f'{prop_name},'
        elif prop_get[i] == False:
            current_prop = f'private {prop_types[i]} _{prop_name};'
        else:
            current_prop = 'public ' + prop_types[i] + " " + prop_name.capitalize() + ' { '
            if prop_get[i]:
                current_prop += f'{get_accessors[i]} get; '
            if prop_set[i]:
                current_prop += f'{set_accessors[i]} set; '
            current_prop += '}'
        property_texts.append(current_prop)
    return property_texts

def capitalize_type(var_type):
    if not any(primitive_type in var_type for primitive_type in PRIMITIVE_TYPES):
            var_type = var_type.capitalize()
    return var_type

def remember_interfaces(sections):
    for section in sections:
        class_block = get_string_between(section,'<{','}>')
        segments = class_block.split('|')
        for segment in segments:
            if '<b>' in segment.lower():
                current_class_name = get_string_between(segment,'<b>','</b>').replace('&lt;','').replace('&gt;','')
                if current_class_name == '': current_class_name =  get_string_between(segment,'<B>','</B>').replace('&lt;','').replace('&gt;','')
                current_class_type = get_class_type(current_class_name)
                current_class_name = normalize_class_name(current_class_name, current_class_type)
                if 'interface' in current_class_type:
                    KNOWN_INTERFACES.append(current_class_name.lower())
def remember_enums(sections):
    for section in sections:
        class_block = get_string_between(section,'<{','}>')
        segments = class_block.split('|')
        for segment in segments:
            if '<b>' in segment.lower():
                current_class_name = get_string_between(segment,'<b>','</b>').replace('&lt;','').replace('&gt;','')
                if current_class_name == '': current_class_name =  get_string_between(segment,'<B>','</B>').replace('&lt;','').replace('&gt;','')
                current_class_type = get_class_type(current_class_name)
                current_class_name = normalize_class_name(current_class_name, current_class_type)
                if 'enum' in current_class_type:
                    NON_NULLABLE_TYPES.append(current_class_name.lower())


def build_method_text(method,class_name,prop_types,prop_names):
    return_type = ' void '
    abstract = ''
    if method.count('<i>') > 0:
        method = method.replace('<i>','').replace('</i>','')
        abstract = 'abstract '
    method, accessor_index = process_accessors(method)
    colon_index = len(method)
    if method.find(':') >= 0:
        colon_index = method.find(':')
        return_type = method[colon_index+1:].lstrip()
        return_type = capitalize_type_correctly(return_type)
    method_text = method[:accessor_index] + abstract + return_type + ' ' + method[accessor_index:colon_index].lstrip()
    method_text = ' '.join(method_text.split())
    (method_text,constructor_assignments) = fill_constructor(method, class_name, prop_types, prop_names, method_text)
    method_text = method_text.strip().replace('  ',' ')
    return  method_text, constructor_assignments

def fill_constructor(method, class_name, prop_types, prop_names, method_text):
    constructor_assignments = []
    if ' ' + class_name.strip().lower() + '(' in method_text.lower():
        method_text = method_text.replace(' void','')
        params = get_string_between(method,'(',')').split(',')
        start = 0
        indexes_already_done = []
        for i, param_type in enumerate(params):
            for j in range(0,len(prop_types)):
                if j in indexes_already_done: continue
                if param_type.strip().lower() == prop_types[j].strip().lower() and param_type != '':
                    null_check = ''
                    if param_type.strip().lower() == 'string':
                        constructor_assignments.append(f'if (string.IsNullOrWhiteSpace({prop_names[j]}))')
                        constructor_assignments.append(f'\t throw new ArgumentNullException(nameof({prop_names[j]}), "{prop_names[j]} cannot be null or empty.");')
                    elif param_type.strip().lower() not in NON_NULLABLE_TYPES or '?' in param_type.strip():
                        null_check = f' ?? throw new ArgumentNullException(nameof({prop_names[j]}),"{prop_names[j]} cannot be null")'
                    params[i] = capitalize_type_correctly(params[i].lstrip())
                    params[i] += ' ' + prop_names[j]
                    constructor_assignments.append(f'{prop_names[j].capitalize()} = {prop_names[j]}{null_check};')
                    indexes_already_done.append(j)
                    break
        method_text = method_text[:method_text.find('(')+1] + ', '.join(params) + method_text[method_text.find(')'):]
    return method_text, constructor_assignments

def process_accessors(method):
    accessor_index = 0
    accessors = [(' public ','+'),(' private ','-'),(' protected ','#'),(' internal ','~')]
    for accessor in accessors:
        name, symbol = accessor
        method = method.replace(symbol,name)
        if method.find(f' {name} ') >= 0:
            accessor_index = method.find(name) + len(name)
            break
    return method,accessor_index
def get_accessor(method):
    accessors = [('private','-'),('protected','#'),('internal','~')]
    for accessor in accessors:
        name, symbol = accessor
        if symbol in method:
            return name
    return ''
def capitalize_type_correctly(type):
    if type.strip() in PRIMITIVE_TYPES:
        return type
    if type.strip().lower() == 'datetime':
        return 'DateTime'
    type = type.lstrip().capitalize()
    if any(interface in type.lower() for interface in KNOWN_INTERFACES):
        return_list = list(type)
        return_list[1] = return_list[1].upper()
        type = ''.join(return_list)
    if '<' in type:
        index_begin = type.find('<')
        index_end = type.find('>')
        inner_type = capitalize_type_correctly(get_string_between(type,'<','>'))
        type = type[:index_begin+1] + inner_type + type[index_end:]
    return type

def get_class_type(class_name):
    if class_name.lower().find('abstract') >= 0:
        return 'abstract class'
    elif class_name.lower().find('interface') >= 0:
        return 'interface'
    elif class_name.lower().find('enum') >= 0:
        return 'enum'
    else:
        return 'class'

def normalize_class_name(class_name, class_type):
    name = class_name.replace('interface','').replace('abstract','').replace('enum','').replace('<','').replace('>','').strip()
    if 'interface' in class_type:
        name_list = list(name)
        name_list[1] = name_list[1].upper()
        return ''.join(name_list)
    return name


def get_file_environment(class_name, class_type):
    namespace = f'namespace {project_name}'
    if class_type == 'interface':
        output_folder = OUTPUT_FOLDER + '/Interfaces/'
        namespace += '.Interfaces'
    elif 'repository' in class_name.lower():
        output_folder = OUTPUT_FOLDER + '/Repositories/'
        namespace += '.Repositories'
    elif 'service' in class_name.lower():
        output_folder = OUTPUT_FOLDER + '/Services/'
        namespace += '.Services/'
    else:
        output_folder = OUTPUT_FOLDER + '/Entities/'
        namespace += '.Entities'
    return output_folder, namespace


def write_files(indent, segments, prop_texts, method_texts):
    file = open(ERROR_FILE,'w')
    for i,segment in enumerate(segments):
        class_name = ''
        if i == 0:
            class_name = get_string_between(segment,'<b>','</b>').replace('&lt;','').replace('&gt;','')
            if class_name == '': class_name =  get_string_between(segment,'<B>','</B>').replace('&lt;','').replace('&gt;','')
            class_type = get_class_type(class_name)
            class_name = normalize_class_name(class_name, class_type)
            if class_name == '':
                continue
            output_folder, namespace = get_file_environment(class_name,class_type)
            os.makedirs(output_folder, exist_ok=True)
            if os.path.exists(output_folder + class_name):
                os.remove(output_folder + class_name)
            file = open(output_folder + class_name + '.cs','w')
            file.write('using System;\n\n')
            file.write(namespace + ';\n\n')
            file.write(f'public {class_type} {class_name}\n' + '{')
            file.write('\n')
            indent += '\t'
    for prop in prop_texts:
        file.write(indent+prop + '\n')
    file.write('\n')
    for m in method_texts:
        if m == '}':
            indent = indent[:-1]
        file.write(indent+m + '\n')
        if m == '{':
            indent += '\t'
    file.write('}')

import_interfaces()
project_name = input('what is the project name?: ')
# project_name = 'test'
os.makedirs("output", exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
sections = get_section()
remember_interfaces(sections)
remember_enums(sections)
for section in sections:
    indent = ''
    if section.find('label') < 0: continue  
    class_block = get_string_between(section,'<{','}>')
    segments = class_block.split('|')
    if class_block == '': continue
    (prop_texts,method_texts) = get_texts(segments)
    write_files(indent, segments, prop_texts, method_texts)
