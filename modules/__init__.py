import os

def find_files_with_extension(extension):
    files_filter = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(extension):
                files_filter.append(os.path.join(root, file))
    return files_filter