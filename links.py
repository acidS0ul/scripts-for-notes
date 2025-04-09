import re
import os
import sys 
import json

LINKS           = 0
BACKLINKS       = 1

def find_files_with_extension(extension):
    files_filter = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(extension):
                files_filter.append(os.path.join(root, file))
    return files_filter

def replace_wiki_links_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    updated_content = []
    for line in content:
        updated_line = re.sub(r'\b\[\[(.*?)\]\]\b', r'[\1](\1.md)', line)
        updated_content.append(updated_line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(''.join(updated_content))

def read_lines_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines

def write_lines_to_file(filename, lines):
    with open(filename, 'w') as file:
        file.writelines(lines)

def add_new_backlinks(info):
    for file in info.keys():
        lines = read_lines_from_file(file)
        backlinks_found = False
        for i, line in enumerate(lines):
            if line.strip() == "backlinks:":
                backlinks_found = True
                for bk in info[file]:
                    lines.insert(i + 1, f"- {bk}\n")
                break
        if backlinks_found == False:
            print(f"In \"{file}\" not found \"backlinks:\" string")
            continue

        write_lines_to_file(file, lines)
                

def find_links(lines):
    backlinks = []
    links = []
    regex = r"^-\s(\[.*\]\(.*\.md\))"
    matches = re.finditer(regex, "".join(lines), re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1 
            backlinks.append(match.group(groupNum))
    matches = re.finditer(regex, "".join(lines), re.MULTILINE)
    regex = r"\[.*\]\(.*\.md\)"
    matches = re.finditer(regex, "".join(lines), re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        links.append(match.group())
    
    for link in links:
        for backlink in backlinks:
            if link == backlink:
                links.remove(link)

    return [links, backlinks]

def format_links(links):
    copy = links
    for link in copy:
        new_link = re.sub(r'\[.*\]\((.*?)\)', r'[\1](\1)', link)        
        links.remove(link)
        links.append(new_link)
    return links


def create_links_database(files):
    links = []
    database = {}
    for file_path in files:
        lines = read_lines_from_file(file_path)
        links = find_links(lines)
        links[LINKS] = format_links(links[LINKS])
        database[os.path.basename(file_path)] = links
    return database

def filename_to_markdown_link(file):
    name = re.sub(r'(.*?).md', r'\1', file)        
    name = name.replace("_", " ")       
    
    return f"[{name}]({file})"

def extract_filename(link):
    filename = re.sub(r'\[.*\]\((.*?)\)', r'\1', link)        
    return filename

def find_new_backlinks(database):
    new_backlinks = {}
    for key in database.keys():
        for link in database[key][LINKS]:
            filename = extract_filename(link)
            is_found = False 
            if not filename in database.keys():
                # FIXME: why not found&
                # print(f"file {filename} not found")
                continue

            if not filename in new_backlinks.keys():
                new_backlinks[filename] = []

            new_backlink = filename_to_markdown_link(key)
            for backlink in database[filename][BACKLINKS]:
                if link in backlink:
                    is_found = True 
                       
            if is_found == False:
                for old_backlink in database[filename][BACKLINKS]:
                    if new_backlink in old_backlink:
                        is_found = True 

            if is_found == False:
                if not new_backlink in new_backlinks[filename]:
                    new_backlinks[filename].append(new_backlink)
                    print(f"new backlink {new_backlink} in {filename} from {key}")

    return  new_backlinks           

if __name__ == "__main__":
    file_extension = '.md'
    files = find_files_with_extension(file_extension)
    database = create_links_database(files)
    # print(json.dumps(database, ensure_ascii=False,  indent=4))
    new_backlinks = find_new_backlinks(database)
    # print(json.dumps(new_backlinks, ensure_ascii=False,  indent=4))
    add_new_backlinks(new_backlinks)

