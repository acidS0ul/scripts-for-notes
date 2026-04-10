import re
import os
from typing import List, Optional, Tuple, Dict, Any

LINKS = 0
BACKLINKS = 1


def read_lines_from_file(filename: str) -> List[str]:
    with open(filename, 'r', encoding='utf-8') as file:
        return file.readlines()


def write_lines_to_file(filename: str, lines: List[str]) -> None:
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(lines)


def find_links(file_path: str) -> Optional[List[List[str]]]:
    """Find wiki links and backlinks in a markdown file.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        List containing [links, backlinks] or None if backlinks section not found
    """
    backlinks = []
    links = []
    lines_before_backlinks = []
    lines_after_backlinks = []
    backlinks_found = False

    lines = read_lines_from_file(file_path)

    for line in lines:
        if not backlinks_found:
            lines_before_backlinks.append(line)
            if line.strip() == "backlinks:":
                backlinks_found = True
        else:
            lines_after_backlinks.append(line)

    if not backlinks_found:
        print(f"In \"{file_path}\" not found \"backlinks:\" string")
        return None

    regex = r"(\[.*\]\(.*\.md\))"
    matches = re.finditer(regex, "".join(lines_after_backlinks), re.MULTILINE)
    for match in matches:
        backlinks.append(match.group(1))

    regex = r"\[.*\]\(.*\.md\)"
    matches = re.finditer(regex, "".join(lines_before_backlinks), re.MULTILINE)
    for match in matches:
        links.append(match.group())

    return [links, backlinks]


def format_links(links: List[str]) -> List[str]:
    """Format markdown links to [filename](filename) format."""
    result = []
    for link in links:
        new_link = re.sub(r'\[.*\]\((.*?)\)', r'[\1](\1)', link)
        result.append(new_link)
    return result


def extract_filename(link: str) -> str:
    """Extract filename from markdown link."""
    return re.sub(r'\[.*\]\((.*?)\)', r'\1', link)


def filename_to_markdown_link(file: str) -> str:
    """Convert filename to markdown link format."""
    name = re.sub(r'(.*?).md', r'\1', file)
    name = name.replace("_", " ")
    return f"[{name}]({file})"


def create_links_database(files: List[str]) -> Dict[str, List[Any]]:
    """Create database of links from all markdown files.
    
    Args:
        files: List of file paths
        
    Returns:
        Dictionary with filename as key and [links, backlinks] as value
    """
    database = {}
    for file_path in files:
        links = find_links(file_path)
        if links is None:
            continue
        links[LINKS] = format_links(links[LINKS])
        database[os.path.basename(file_path)] = links
    return database


def find_new_backlinks(database: Dict[str, List[Any]], verbose: bool = False) -> Dict[str, List[str]]:
    """Find new backlinks that should be added to files.
    
    Args:
        database: Links database from create_links_database
        verbose: Enable verbose logging
        
    Returns:
        Dictionary with filename as key and list of new backlinks as value
    """
    new_backlinks = {}
    for key in database.keys():
        for link in database[key][LINKS]:
            filename = extract_filename(link)
            if filename not in database.keys():
                continue

            if filename not in new_backlinks.keys():
                new_backlinks[filename] = []

            new_backlink = filename_to_markdown_link(key)
            is_found = False
            
            for backlink in database[filename][BACKLINKS]:
                if link in backlink:
                    is_found = True

            if not is_found:
                for old_backlink in database[filename][BACKLINKS]:
                    if new_backlink in old_backlink:
                        is_found = True

            if not is_found and new_backlink not in new_backlinks[filename]:
                new_backlinks[filename].append(new_backlink)
                if verbose:
                    print(f"new backlink {new_backlink} in {filename} from {key}")

    return new_backlinks


def add_new_backlinks(info: Dict[str, List[str]]) -> None:
    """Add new backlinks to files.
    
    Args:
        info: Dictionary with filename as key and list of backlinks to add
    """
    for file in info.keys():
        lines = read_lines_from_file(file)
        backlinks_found = False
        for i, line in enumerate(lines):
            if line.strip() == "backlinks:":
                backlinks_found = True
                for bk in info[file]:
                    lines.insert(i + 1, f"- {bk}\n")
                break
        if not backlinks_found:
            print(f"In \"{file}\" not found \"backlinks:\" string")
            continue

        write_lines_to_file(file, lines)