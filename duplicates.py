# -*- coding: utf-8 -*-

'''
This code was taken from Todor Minakov's answer on this Stack Overflow
post:
            748675/finding-duplicate-files-and-removing-them
Although I had to correct a minor error and actually the code that
deletes the duplicate files.
'''

from collections import defaultdict
import hashlib
import os
import sys


def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes.
    
    Args:
        fobj (obj):
            The file object to read chunks of.
    
    Kwargs:
        chunk_size (int, 1024):
            The size of each chunk to read. The default is 1024.
    """

    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash=hashlib.sha1):
    """

    """

    hashobj = hash()
    file_object = open(filename, 'rb')

    if first_chunk_only:
        hashobj.update(file_object.read(1024))
    else:
        for chunk in chunk_reader(file_object):
            hashobj.update(chunk)
    hashed = hashobj.digest()

    file_object.close()
    return hashed


def check_for_duplicates(path, hash=hashlib.sha1):
    """

    """

    # Dictionary of size_in_bytes: [full_path_to_file1, ...]
    hashes_by_size = defaultdict(list)
    # Dictionary of (hash1k, size_in_bytes): [full_path_to_file1, ...]
    hashes_on_1k = defaultdict(list)
    # Dictionary of full_file_hash: full_path_to_file_string
    hashes_full = {}

    for dirpath, dirnames, filenames in os.walk(path):
        # Get all files with the same size - they are the collision candidates
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            try:
                # If the target is a symlink (soft one), this will 
                # dereference it - change the value to the actual target file
                full_path = os.path.realpath(full_path)
                file_size = os.path.getsize(full_path)
                hashes_by_size[file_size].append(full_path)
            except (OSError,):
                # Ignore if the file is not accessible due to permissions, etc.
                continue

    # For files with the same size, get their hash on the 1st 1024 bytes only
    for size_in_bytes, files in hashes_by_size.items():
        if len(files) < 2:
            # This file size is unique, no need to spend CPU cycles on it
            continue 

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
                # The key is the hash on the first 1024 bytes plus the size - to
                # avoid collisions on equal hashes in the first part of the file
                # --- Credits to @Futal for the optimization
                hashes_on_1k[(small_hash, size_in_bytes)].append(filename)
            except (OSError,):
                # The file access might've changed before reaching this point 
                continue

    # Initialize the duplicates variables, which is a list of sets
    duplicates = []

    # For all files with the hash on the 1st 1024 bytes, get their hash on the
    # full file - collisions will be duplicates
    for _, files_list in hashes_on_1k.items():
        if len(files_list) < 2:
            # This hash is unique, no need to spend CPU cycles on it
            continue

        for filename in files_list:
            try: 
                full_hash = get_hash(filename, first_chunk_only=False)
                duplicate = hashes_full.get(full_hash)
                if duplicate:
                    for g, group in enumerate(duplicates):
                        if os.path.basename(filename) in group or os.path.basename(duplicate) in group:
                            duplicates[g].add(os.path.basename(filename))
                            duplicates[g].add(os.path.basename(duplicate))
                            break
                    else:
                        duplicates.append({os.path.basename(filename), os.path.basename(duplicate)})
                else:
                    hashes_full[full_hash] = filename
            except (OSError,):
                # The file access might've changed before reaching this point 
                continue
    
    return duplicates


def remove_duplicates(path, duplicates):
    """

    """

    for group in duplicates:
        group.pop()
        for d in group:
            os.remove(os.path.join(path, d))


if __name__ == "__main__":
    # Changed slice from [1:] to [1] to only check in one directory
    if sys.argv[1]:
        check_for_duplicates(sys.argv[1])
    else:
        print("Please pass the paths to check as parameters to the script")