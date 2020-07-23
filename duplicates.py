# -*- coding: utf-8 -*-

'''
This code was taken from Todor Minakov's answer on this Stack Overflow
post:
            748675/finding-duplicate-files-and-removing-them
Although I had to correct a minor error and actually the code that
deletes the duplicate files.
'''

# if running in py3, change the shebang, drop the next import for readability (it does no harm in py3)
from collections import defaultdict
import hashlib
import os
import sys


def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash=hashlib.sha1):
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


def check_for_duplicates(paths, hash=hashlib.sha1):
    hashes_by_size = defaultdict(list)  # dict of size_in_bytes: [full_path_to_file1, full_path_to_file2, ]
    hashes_on_1k = defaultdict(list)  # dict of (hash1k, size_in_bytes): [full_path_to_file1, full_path_to_file2, ]
    hashes_full = {}   # dict of full_file_hash: full_path_to_file_string

    for path in paths:
        # print(path)
        for dirpath, dirnames, filenames in os.walk(path):
            # get all files that have the same size - they are the collision candidates
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                try:
                    # if the target is a symlink (soft one), this will 
                    # dereference it - change the value to the actual target file
                    full_path = os.path.realpath(full_path)
                    file_size = os.path.getsize(full_path)
                    hashes_by_size[file_size].append(full_path)
                except (OSError,):
                    # not accessible (permissions, etc) - pass on
                    continue


    # For all files with the same file size, get their hash on the 1st 1024 bytes only
    for size_in_bytes, files in hashes_by_size.items():
        if len(files) < 2:
            continue    # this file size is unique, no need to spend CPU cycles on it

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
                # the key is the hash on the first 1024 bytes plus the size - to
                # avoid collisions on equal hashes in the first part of the file
                # credits to @Futal for the optimization
                hashes_on_1k[(small_hash, size_in_bytes)].append(filename)
            except (OSError,):
                # the file access might've changed till the exec point got here 
                continue

    # duplicates = {}
    # n_duplicates = 0
    duplicates = []

    # For all files with the hash on the 1st 1024 bytes, get their hash on the full file - collisions will be duplicates
    for test, files_list in hashes_on_1k.items():
        # print(len(files_list))
        # if len(files) < 2:
        if len(files_list) < 2:
            continue    # this hash of fist 1k file bytes is unique, no need to spend cpy cycles on it

        directory = os.path.dirname(files_list[0])
        print(test)
        for filename in files_list:
            print(files_list)
            # print(filename)
            try: 
                full_hash = get_hash(filename, first_chunk_only=False)
                duplicate = hashes_full.get(full_hash)
                if duplicate:
                    # n_duplicates += 1
                    # print("Duplicate found: {} and {}".format(os.path.basename(filename), os.path.basename(duplicate)), end='\n\n')
                    
                    
                    for g, group in enumerate(duplicates):
                        if os.path.basename(filename) in group or os.path.basename(duplicate) in group:
                            duplicates[g].add(os.path.basename(filename))
                            duplicates[g].add(os.path.basename(duplicate))
                            break
                    else:
                        duplicates.append({os.path.basename(filename), os.path.basename(duplicate)})
                    
                    # for g, group in enumerate(duplicates):
                    #     if filename in group or duplicate in group:
                    #         duplicates[g].add(filename)
                    #         duplicates[g].add(duplicate)
                    # else:
                    #     duplicates.append({filename, duplicate})

                else:
                    hashes_full[full_hash] = filename
            except (OSError,):
                # the file access might've changed till the exec point got here 
                continue
        print('\n')
    
    # return duplicates
    # print(f'There are {n_duplicates} duplicates in the folder.', end='\n\n')

    # for k, v in duplicates.items(): print(f'{k}: {v}', end='\n\n')
    # print(duplicates)
    # all_dupes = set()
    for group in duplicates:
        spared = group.pop()
        for d in group:
            os.remove(os.path.join(directory, d))

    # total = 0
    # print(f'There are {len(duplicates)} sets.')
    # for group in duplicates:
    #     print(group)
    #     # # print(f'Before: {len(group)}')
    #     spared = group.pop()
    #     print(f'Spared {spared} from deletion.')
    #     # # print(f'After: {len(group)}')
    #     for d in group:
    #         total += 1
    #         print(f'Removing {d}...')
    #     #     # all_dupes.add(d)
    #         # os.remove(d)
    #         os.remove(os.path.join(directory, d))

        # print('\n')
    # print(len(all_dupes))
    # print(f'There are {total} items in total.', end='\n\n')



if __name__ == "__main__":
    if sys.argv[1:]:
        check_for_duplicates(sys.argv[1:])
    else:
        print("Please pass the paths to check as parameters to the script")