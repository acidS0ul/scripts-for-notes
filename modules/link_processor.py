import re
import os


def replace_in_file(file_path: str, rg1: str, rg2: str) -> None:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    updated_content = []
    for line in content:
        updated_line = re.sub(rg1, rg2, line)
        updated_content.append(updated_line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(''.join(updated_content))


def replace_wiki_links_in_file(file_path: str) -> None:
    """Convert [[wiki]] links to markdown [wiki](wiki.md)"""
    replace_in_file(file_path, r'\[\[(.*?)\]\]', r'[\1](\1.md)')


def replace_media_wiki_links_in_file(file_path: str) -> None:
    """Convert ![]([[media]]) to markdown ![](media)"""
    replace_in_file(file_path, r'!\[\[(.*)\]\]', r'![\1](\1)')


def fix_media_path_in_file(file_path: str, root_dir: str, verbose: bool = False) -> bool:
    """Fix media file paths in markdown files.
    
    Args:
        file_path: Path to the markdown file
        root_dir: Root directory to check for media files
        verbose: Enable verbose logging
        
    Returns:
        True if successful, False if error occurred
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    updated_content = []
    for line in content:
        match = re.search(r"!\[.*\]\((.*)\)", line)
        if match:
            filename = match.group(1)
            if verbose:
                print(f"filename:{filename}")
            if os.path.exists(filename):
                if verbose:
                    print(f"{filename} exists")
                updated_content.append(line)
                continue
            if os.path.exists(root_dir + filename):
                updated_line = re.sub(
                    re.escape(filename),
                    re.escape(root_dir + filename),
                    line
                )
                if verbose:
                    print(f"updated line: {updated_line}")
                updated_content.append(updated_line)
            else:
                print(f"error: {root_dir + filename}, not found")
                return False
        else:
            updated_content.append(line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(''.join(updated_content))
    
    return True