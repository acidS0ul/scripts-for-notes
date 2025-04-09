import os


def find_files_with_extension(extension):
    files_filter = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(extension):
                files_filter.append(os.path.join(root, file))
    return files_filter

def find_files_with_extension(extension):
    files_filter = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(extension):
                files_filter.append(os.path.join(root, file))
    return files_filter

if __name__ == "__main__":
    print(find_files_with_extension(".md"))
