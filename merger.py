#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from typing import Dict, List, Tuple


def md5(file_path: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def list_files(directory: str, dir_number: int) -> Tuple[str, Dict[str, str]]:
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


def find_duplicates(files: List[Tuple[str, Dict[str, str]]]) -> Dict[str, List[str]]:
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


def remove_duplicates(
        duplicates: Dict[str, List[str]],
        keeper: str,
        keep_shortest: bool = False,
        dry_run: bool = False
) -> None:
    removed_files = []
    for hash, files in duplicates.items():
        is_in_keeper = any(map(lambda f: f.startswith(keeper), files))
        shortest = min(files, key=len)
        for file in files:
            if (
                    (not file.startswith(keeper) and is_in_keeper) or
                    (keep_shortest and file != shortest)
            ):
                print('delete', file)
                removed_files.append(file)
                if not dry_run:
                    os.remove(file)
    with open('removed.json', 'w') as f:
        json.dump(removed_files, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry-run', dest='dry', default=False, action='store_true',
                        help='don\'t actually remove anything')
    parser.add_argument('dir', nargs='+', help='directory', type=str)
    args = parser.parse_args()
    files = []
    for i, directory in enumerate(args.dir):
        files.append(list_files(directory, i))
    duplicates = find_duplicates(files)
    remove_duplicates(duplicates, args.dir[0], keep_shortest=len(args.dir) == 1, dry_run=args.dry)
