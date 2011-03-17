
import os, fnmatch

# From Python Cookbook, 2nd ed., by Alex Martelli, Anna Martelli
# Ravenscroft, and David Ascher (O'Reilly Media, 2005) 0-596-00797-3
def all_files(root, patterns='*', single_level=False, yield_folders=False):
    # Expand patterns from semicolon-separated string to list
    patterns = patterns.split(';')
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
                    break
        if single_level:
            break
