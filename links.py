import re
import os
import sys 

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

def add_line_after_backlinks(lines):
    for i, line in enumerate(lines):
        if line.strip() == "backlinks:":
            lines.insert(i + 1, "test\n")
            break

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
                # print(f"removed {backlink} in {links}")
                links.remove(link)

    return [links, backlinks]

def format_links(links):
    copy = links
    for link in copy:
        new_link = re.sub(r'\[.*\]\((.*?)\)', r'[\1](\1)', link)        
        links.remove(link)
        links.append(new_link)
        # print(f"old link {link}\nnew link {new_link}")
    return links


def create_links_database(files):
    links = []
    database = {}
    for file_path in files:
        lines = read_lines_from_file(file_path)
        links = find_links(lines)
        links[LINKS] = format_links(links[LINKS])
        database[os.path.basename(file_path)] = links

    # print(database)
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
            if not filename in database:
                # FIXME: why not found&
                # print(f"file {filename} not found")
                continue

            new_backlinks[filename] = []
            for backlink in database[filename][BACKLINKS]:
                if link == backlink:
                    is_found = True 

            if is_found == False:
                print(f"new backlink {key} for {filename}")
                new_backlinks[filename].append(filename_to_markdown_link(key))
    print(new_backlinks)
                

if __name__ == "__main__":
    file_extension = '.md'
    files = find_files_with_extension(file_extension)
    database = create_links_database(files)
    find_new_backlinks(database)
    
    # for file_path in files:
    #     replace_wiki_links_in_file(file_path)


