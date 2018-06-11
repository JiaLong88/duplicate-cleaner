# -*- coding: utf-8 -*-

import argparse
import os
import sys
from hashlib import md5
from pathlib import Path
from iterview import iterview

MIN_SIZE = 8192


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='target directory')
    parser.add_argument('-i', '--interactive', default=False, const=True, action='store_const',
                        help='Interactively choose file deletion')

    parser.add_argument('-f', '--force', default=False, const=True, action='store_const',
                        help='Delete all duplicate files without asking')

    args = parser.parse_args()
    return args


def list_all_duplicates(directory):
    target = Path(directory)

    print ('[*] finding all files...')
    filenames = target.glob('**/*')

    files = [f for f in filenames]
    files = sorted(files, key=lambda x: x.stat().st_size)
    files = list(filter(lambda x: x.stat().st_size > MIN_SIZE, files))

    hashes = {}
    first = None
    cur_size = -1
    for file in iterview(files):

        if file.is_dir():
            continue

        size = file.stat().st_size
        if cur_size == size:

            # if two same size files are found, record first one,
            if first is not None:
                with first.open('rb') as f:
                    hashval = md5(f.read()).hexdigest()
                    hashes[hashval] = [first]
                    first = None

            with file.open('rb') as f:
                hashval = md5(f.read()).hexdigest()
                if hashes.get(hashval):
                    hashes[hashval].append(file)
                else:
                    hashes[hashval] = [file]
        else:
            first = file
            cur_size = size

    dup_files_list = []
    for paths in hashes.values():
        if len(paths) > 1:
            dup_files_list.append(paths)

    return dup_files_list


def main():

    args = parse_args()

    dup_files_list = list_all_duplicates(args.directory)

    print('[*] found {num} duplicate files'.format(num=len(dup_files_list)))

    if args.interactive:
        print('[-] NOT IMPLEMENTED')
        for dup_files in dup_files_list:
            pass
    else:
        if not args.force:
            choice = input('[*] Remove duplicate files (Y/N)?').strip().upper()
        if args.force or choice == 'Y':
            for dup_files in dup_files_list:
                print('\n[*] original: {}'.format(str(dup_files[0])))
                for dup in dup_files[1:]:
                    print('   ---> duplicate: {}'.format(str(dup)))
                    dup.unlink()

if __name__ == '__main__':
    main()