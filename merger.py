#!/usr/bin/env python3
import argparse
import hashlib
import os
import json


def md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def list_files(directory, dir_number):
    cache_file_name = 'dir{}_cache.json'.format(dir_number)
    file_list = {}
    if os.path.isfile(cache_file_name):
        with open(cache_file_name) as f:
            file_list = json.load(f)
    else:
        for subdir, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(subdir, file)
                print('reading', file_path)
                file_list[file_path] = md5(file_path)
        with open(cache_file_name, 'w') as f:
            json.dump(file_list, f, indent=4, sort_keys=True)
    return directory, file_list


def find_duplicates(files):
    file_dict_only_duplicates = {}
    duplicates_json_file_name = 'duplicates.json'
    if os.path.isfile(duplicates_json_file_name):
        with open(duplicates_json_file_name) as f:
            file_dict_only_duplicates = json.load(f)
    else:
        file_dict = {}
        for directory, file_list in files:
            for file_path, file_hash in file_list.items():
                try:
                    file_dict[file_hash].append(file_path)
                except KeyError:
                    file_dict[file_hash] = [file_path]
        for hash, files in file_dict.items():
            if len(files) > 1:
                file_dict_only_duplicates[hash] = files
        print('Number of files with duplicates:', len(file_dict_only_duplicates.keys()))
        with open('duplicates.json', 'w') as f:
            json.dump(file_dict_only_duplicates, f, indent=4, sort_keys=True)
    return file_dict_only_duplicates


def remove_duplicates(duplicates, keeper):
    removed_files = []
    for hash, files in duplicates.items():
        is_in_keeper = any(map(lambda f: f.startswith(keeper), files))
        for file in files:
            if not file.startswith(keeper) and is_in_keeper:
                print('delete', file)
                removed_files.append(file)
                os.remove(file)
    with open('removed.json', 'w') as f:
        json.dump(removed_files, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', nargs='+', help='directory', type=str)
    args = parser.parse_args()
    files = []
    for i, directory in enumerate(args.dir):
        files.append(list_files(directory, i))
    duplicates = find_duplicates(files)
    remove_duplicates(duplicates, args.dir[0])
