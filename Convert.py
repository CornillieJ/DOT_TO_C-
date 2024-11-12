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
        if(is_line_relevant(line)):
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
    methods_included = []
    methods_texts=[]
    is_interface = False
    for i,segment in enumerate(class_segments):
        segment = segment.replace('&lt;','<').replace('&gt;','>')
        if i == 0: 
            current_class_name = get_string_between(segment,'<b>','</b>').replace('&lt;','').replace('&gt;','')
            current_class_type = get_class_type(current_class_name)
            current_class_name = normalize_class_name(current_class_name, current_class_type) 
            if 'interface' in segment:
                is_interface = True
            continue
        if i == 1 and is_interface == False:
            properties = segment.splitlines()
            for property in properties:
                if property == '': continue
                property = property.replace(' ','')
                prop_names.append(get_string_between(property,'-',':'))
                prop_types.append(property[property.find(':')+1:])
                prop_set.append(False)
                prop_get.append(False)
        else:
            methods = segment.splitlines()
            if is_interface == True:
                is_interface = False
            for m,method in enumerate(methods):
                methods_included.append(False)
                if method.strip().strip('\n') == '': continue
                methods_included[m] = True
                for j,prop_name in enumerate(prop_names):
                    method = method.replace('&lt;','<').replace('&gt;','>')
                    if method.find('get' + prop_name)>= 0:
                        methods_included[m] = False
                        prop_set[j] = True
                    if method.find('set' + prop_name)>= 0:
                        methods_included[m] = False
                        prop_get[j] = True
                if methods_included[m]:
                    (method_text,constructor_assignments) = build_method_text(method,current_class_name,prop_types, prop_names)
                    methods_texts.append(method_text)
                    methods_texts.append('{')
                    for assignment in constructor_assignments:
                        methods_texts.append(assignment)
                    methods_texts.append('}')
                    
    property_texts = build_properties(prop_names, prop_types, prop_get, prop_set)
    return (property_texts,methods_texts)

def build_properties(prop_names, prop_types, prop_get, prop_set):
    property_texts = []
    for i, prop_name in enumerate(prop_names):
        current_prop = []
        if prop_name == '' or prop_types[i] == '': 
            continue
        prop_types[i] = capitalize_type_correctly(prop_types[i])
        if prop_get[i] == False and prop_set[i] == False:
            current_prop = f'private {prop_types[i]} _{prop_name};'
        else:
            current_prop = 'public ' + prop_types[i] + " " + prop_name.capitalize() + ' { '
            if prop_get[i]:
                current_prop += 'get; '
            if prop_set[i]:
                current_prop += 'set; '
            current_prop += '}'
        property_texts.append(current_prop)
    return property_texts

def capitalize_type(type):
    if not any(primitive_type in type for primitive_type in PRIMITIVE_TYPES):
            type = type.capitalize()
    return type

def remember_interfaces(sections):
    for section in sections:
        class_block = get_string_between(section,'<{','}>').lower()
        segments = class_block.split('|')
        for segment in segments:
            if '<b>' in segment:
                current_class_name = get_string_between(segment,'<b>','</b>').replace('&lt;','').replace('&gt;','')
                current_class_type = get_class_type(current_class_name)
                current_class_name = normalize_class_name(current_class_name, current_class_type)
                if 'interface' in current_class_type:
                    KNOWN_INTERFACES.append(current_class_name.lower())

def build_method_text(method,class_name,prop_types,prop_names):
    return_type = ' void '
    abstract = ''
    if method.count('<i>') > 0:
        method = method.replace('<i>','').replace('</i>','')
        abstract = 'abstract '
    method, accessorIndex = process_accessors(method)
    colon_index = len(method)
    if method.find(':') >= 0:
        colon_index = method.find(':')
        return_type = method[colon_index+1:].lstrip()
        return_type = capitalize_type_correctly(return_type)
    method_text = method[:accessorIndex] + abstract + return_type + ' ' + method[accessorIndex:colon_index].lstrip().capitalize()
    method_text = ' '.join(method_text.split())
    (method_text,constructor_assigments) = fill_constructor(method, class_name, prop_types, prop_names, method_text)
    method_text = method_text.strip().replace('  ',' ')
    return (method_text,constructor_assigments)

def fill_constructor(method, class_name, prop_types, prop_names, method_text):
    constructor_assignments = []
    if class_name.lower() + '(' in method_text.lower():
        method_text = method_text.replace(' void','')
        params = get_string_between(method,'(',')').split(',')
        start = 0
        for i, param_type in enumerate(params):
            for j in range(start,len(prop_types)):
                if param_type.strip() in prop_types[j] and param_type != '':
                    null_check = ''
                    if param_type.strip() not in NON_NULLABLE_TYPES or '?' in param_type.strip():
                        null_check = f' ?? throw new ArgumentNullException("{prop_names[j]} cannot be null")'
                    params[i] = capitalize_type_correctly(params[i].lstrip())
                    params[i] += ' ' + prop_names[j]
                    constructor_assignments.append(f'{prop_names[j].capitalize()} = {prop_names[j]}{null_check};\n')
                    start = j+1
                    break
        method_text = method_text[:method_text.find('(')+1] + ', '.join(params) + method_text[method_text.find(')'):]
    return (method_text, constructor_assignments)

def process_accessors(method):
    accessorIndex = 0
    accessors = [(' public ','+'),(' private ','-'),(' protected ','#'),(' internal ','~')]
    for accessor in accessors:
        name, symbol = accessor
        method = method.replace(symbol,name)
        if method.find(f' {name} ') >= 0:
            accessorIndex = method.find(name) + len(name)
            break
    return method,accessorIndex

def capitalize_type_correctly(type):
    if type.strip() in PRIMITIVE_TYPES:
        return type
    if(type.strip().lower() == 'datetime'):
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
    else:
        return 'class'

def normalize_class_name(class_name, class_type):
    name = class_name.replace('interface','').replace('abstract','').strip().capitalize()
    if 'interface' in class_type:
        name_list = list(name)
        name_list[1] = name_list[1].upper()
        return ''.join(name_list)
    return name

def write_files(output_folder, get_string_between, get_class_type, normalize_class_name, indent, segments, prop_texts, method_texts):
    file = open(ERROR_FILE,'w')
    for i,segment in enumerate(segments):
        class_name = ''
        if(i == 0):
            class_name = get_string_between(segment,'<b>','</b>').replace('&lt;','').replace('&gt;','')
            class_type = get_class_type(class_name)
            class_name = normalize_class_name(class_name, class_type) 
            if class_name == '':
                continue
            if os.path.exists(output_folder + class_name):
                os.remove(output_folder + class_name)
            file = open(output_folder + class_name + '.cs','w')
            file.write(f'Public {class_type} {class_name}\n' + '{')
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




os.makedirs("output", exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
sections = get_section()
remember_interfaces(sections)
for section in sections:
    indent = ''
    if section.find('label') < 0: continue  
    class_block = get_string_between(section,'<{','}>').lower()
    segments = class_block.split('|')
    if class_block == '': continue
    (prop_texts,method_texts) = get_texts(segments)
    write_files(OUTPUT_FOLDER, get_string_between, get_class_type, normalize_class_name, indent, segments, prop_texts, method_texts)
