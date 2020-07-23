# -*- coding: utf-8 -*-

'''
Checks for duplicates in a specified directory and provides the ability 
to delete them as well.

The foundation of this code was taken from Todor Minakov's answer on
this Stack Overflow post:

stackoverflow.com/questions/748675/finding-duplicate-files-and-removing-them

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
    """Get the hash of the specified file.

    Args:
        filename (str):
            The name of the file.

    Kwargs:
        first_chunk_only (bool, False):
            Whether or not to read only the first chunk of the file.
        hash (hashlib.sha1):
            This argument should be ignored.
    
    Returns:
        The hash of the specified file.
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
    """Checks for duplicate files in the specified directory.

    Args:
        path (str):
            The path of the directory where the duplicate files are
            stored.

    Kwargs:
        hash (hashlib.sha1):
            This argument should be ignored.

    Returns:
        A list of sets, where each set is a group of duplicate files.
        The items of each set are the filename of the duplicate file,
        i.e. without the directory.
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
                    # Create a set for each group of duplicates
                    for g, group in enumerate(duplicates):
                        original_path = os.path.basename(filename)
                        duplicate_path = os.path.basename(duplicate)
                        if original_path in group or duplicate_path in group:
                            duplicates[g].add(original_path)
                            duplicates[g].add(duplicate_path)
                            break
                    else:
                        duplicates.append({original_path, duplicate_path})
                else:
                    hashes_full[full_hash] = filename
            except (OSError,):
                # The file access might've changed before reaching this point 
                continue
    
    return duplicates


def remove_duplicates(directory, duplicates):
    """Remove all duplicate files from a given list of duplicate groups.

    Args:
        directory (str):
            The directory where the duplicate files are stored.
        duplicates (list(set)):
            A list of sets, where each set is a group of duplicate
            files. The items of each set are the filename of the 
            duplicate file, i.e. without the directory.

            Will typically be returned by check_for_duplicates.
    """

    for group in duplicates:
        # Pop from the group to keep at least one copy of the file
        group.pop()
        for d in group:
            os.remove(os.path.join(directory, d))
