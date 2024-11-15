import os
import sys

if len(sys.argv) > 1:
    FILE_PATH = sys.argv[1]
else:
    FILE_PATH = 'dot.dot'
INTERFACE_FILE = 'interfaces_import.txt'
IGNORE_LIST = ['digraph','fontname','fontsize','rankdir','node', 'edge']
PRIMITIVE_TYPES = ['string','int','double','decimal','float','bool','long','void']
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

sections = get_section()
remember_interfaces(sections)
file = open(INTERFACE_FILE, 'a')
file_read = open(INTERFACE_FILE, 'r')
interfaces_in_file = file_read.read()
for interface in KNOWN_INTERFACES:
    if interface in interfaces_in_file: continue
    file.write(interface + '\n')