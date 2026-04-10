import argparse
import os
import sys
from typing import List, Optional

from modules import file_utils
from modules import link_processor
from modules import backlinks


def find_files_with_extension(extension: str, root: str = '.') -> List[str]:
    """Find all files with given extension starting from root directory."""
    files_filter = []
    for root_dir, dirs, files in os.walk(root):
        for file in files:
            if file.endswith(extension):
                files_filter.append(os.path.join(root_dir, file))
    return files_filter


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Manage markdown links and backlinks'
    )
    parser.add_argument(
        '-w', '--wiki',
        action='store_true',
        help='Replace wiki links [[name]] with markdown [name](name.md)'
    )
    parser.add_argument(
        '-b', '--back',
        action='store_true',
        help='Update backlinks in files'
    )
    parser.add_argument(
        '-p', '--path',
        metavar='PATH',
        help='Root path for media files'
    )
    parser.add_argument(
        '-d', '--dir',
        metavar='DIR',
        help='Change working directory'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args(argv)

    if args.dir:
        try:
            os.chdir(args.dir)
            if args.verbose:
                print(f"Changed work dir: {os.getcwd()}")
        except FileNotFoundError:
            print(f"Error: dir {args.dir} not found.")
            return 1
        except PermissionError:
            print(f"Error: PermissionError {args.dir}.")
            return 1

    file_extension = '.md'
    files = find_files_with_extension(file_extension)

    if args.path:
        for file in files:
            link_processor.fix_media_path_in_file(file, args.path, args.verbose)

    if args.wiki:
        for file in files:
            if args.verbose:
                print(file)
            link_processor.replace_wiki_links_in_file(file)
            link_processor.replace_media_wiki_links_in_file(file)

    if args.back:
        database = backlinks.create_links_database(files)
        new_backlinks = backlinks.find_new_backlinks(database, args.verbose)
        backlinks.add_new_backlinks(new_backlinks)

    return 0


if __name__ == "__main__":
    sys.exit(main())