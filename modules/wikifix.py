import re
import os

def replace_wiki_links_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    updated_content = []
    for line in content:
        updated_line = re.sub(r'\[\[(.*?)\]\]', r'[\1](\1.md)', line)
        # TODO: add find original file
        # updated_line = re.sub(r'\((.+)\.md\)', lambda m: f"({m.group(1).replace(' ', '')+'.md'})", updated_line)
        updated_content.append(updated_line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(''.join(updated_content))
