import re
import os
import sys 
import json
import getopt

LINKS           = 0
BACKLINKS       = 1

verbose = False

def print_log(s):
    global verbose
    if verbose:
        print(s)

def find_files_with_extension(extension):
    files_filter = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(extension):
                files_filter.append(os.path.join(root, file))
    return files_filter

def replace_in_file(file_path, rg1, rg2):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    updated_content = []
    for line in content:
        updated_line = re.sub(rg1, rg2, line)
        updated_content.append(updated_line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(''.join(updated_content))

def replace_wiki_links_in_file(file_path):
    replace_in_file(file_path, r'\b\[\[(.*?)\]\]\b', r'[\1](\1.md)')

def replace_media_wiki_links_in_file(file_path):
    replace_in_file(file_path, r'\!\[\[(.*)\]\]', r'![\1](\1)')

def read_lines_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines

def fix_media_path_in_file(file_path, root_dir):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()
    
    changed = False

    updated_content = []
    for line in content:
        match = re.search(r"!\[.*\]\((.*)\)", line)
        if match:
            filename = match.group(1)
            print_log(f"filename:{filename}") 
            if os.path.exists(filename):
                print_log(f"{filename} exits")
                updated_content.append(line)
                continue
            if os.path.exists(root_dir + filename):
                updated_line = re.sub(re.escape(filename), 
                                      re.escape(root_dir + filename), line)
                print_log(f"updated line: {updated_line}")
                updated_content.append(updated_line)
            else:
                print(f"error: {root_dir + filename}, not found")
                return
        else:
            updated_content.append(line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(''.join(updated_content))

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
                

def find_links(file_path):
    backlinks = []
    links = []
    lines_before_backlinks = [] 
    lines_after_backlinks = [] 
    backlinks_found = False

    lines = read_lines_from_file(file_path)

    for i, line in enumerate(lines):
        if backlinks_found == False:
            lines_before_backlinks.append(line)
            if line.strip() == "backlinks:":
                backlinks_found = True
        else:
            lines_after_backlinks.append(line)

    if backlinks_found == False:
        print(f"In \"{file_path}\" not found \"backlinks:\" string")
        return [] 

    regex = r"(\[.*\]\(.*\.md\))"
    matches = re.finditer(regex, "".join(lines_after_backlinks), re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1 
            backlinks.append(match.group(groupNum))

    regex = r"\[.*\]\(.*\.md\)"
    matches = re.finditer(regex, "".join(lines_before_backlinks), re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        links.append(match.group())
    
    #for link in links:
    #    for backlink in backlinks:
    #        if link == backlink:
    #            links.remove(link)

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
        links = find_links(file_path)
        if links == []:
            continue
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

def usage():
    print("-h --help - this message")
    print("-w --wiki - replace wiki links")
    print("-v        - verbose")
    print("-b --back - update backlinks")
    print("-d --dir  - directory with files")


def main():
    global verbose
    file_extension = '.md'
    path = '.'

    option_wiki = False
    option_path = False
    option_back = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   "hwvbp:d:", 
                                   ["help", "wiki", "back", "path=", "dir="])
    except getopt.GetoptError as err:
        print(err)
        usage(2)

    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-p", "--path"):
            option_path = True
            path = a
        elif o in ("-w", "--wiki"):
            option_wiki = True
        elif o in ("-d", "--dir"):
            try:
                # Изменение текущей рабочей директории
                os.chdir(a)
                print(f"Change work dir: {os.getcwd()}")
            except FileNotFoundError:
                print(f"Error: dir {a} not found.")
            except PermissionError:
                print(f"Error: PermissionError {a}.")
        elif o in ("-b", "--back"):
            option_back = True
        else:
            assert False, "unhandled option"

    files = find_files_with_extension(file_extension)

    if option_path == True: 
        for file in files:
            fix_media_path_in_file(file, path)

    if option_wiki == True:
        for file in files:
            print_log(file)
            replace_wiki_links_in_file(file)
            replace_media_wiki_links_in_file(file)

    if option_back == True:
        database = create_links_database(files)
        new_backlinks = find_new_backlinks(database)
        print_log(json.dumps(new_backlinks, ensure_ascii=False,  indent=4))
        add_new_backlinks(new_backlinks)

if __name__ == "__main__":
    main()
