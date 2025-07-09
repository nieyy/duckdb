#!/usr/bin/python

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED

BUILD_PATH = os.path.join(os.path.abspath(sys.path[0]), "build")
BUILD_PATH = os.path.join(BUILD_PATH, "tidy")
SCRIPTS_PATH = os.path.join(os.path.abspath(sys.path[0]), "scripts")
CLANG_TIDY = os.path.join(SCRIPTS_PATH, "clang-tidy")
RUN_CLANG_TIDY = os.path.join(SCRIPTS_PATH, "run-clang-tidy.py")
CLANG_TIDY_DIFF = os.path.join(SCRIPTS_PATH, "clang-tidy-diff.py")
CLANG_APPLY_REPLACEMENTS = os.path.join(SCRIPTS_PATH, "clang-apply-replacements")

# Note: need to update the base revision no after upgraded to a
# new percona server version
GIT_BASE_REVISION_TAG = "0b83e5d2f68bc02dfefde74b846bd039f078affa"


def clang_tidy_file(arg):
    if not os.path.isfile(arg):
        print("Unknown file name " + arg)
        return

    if not ".cpp" in arg:
        print(arg + " is not a regular C++ source file name (.cpp)")
        return

    cmd = "git cat-file -e " + GIT_BASE_REVISION_TAG + ":" + arg
    exit_code = subprocess.call(cmd, shell=True)
    if exit_code == 0:
        # This is a file already contained in base revision
        cmd = "git diff -U0 " + GIT_BASE_REVISION_TAG
        cmd += " -- " + arg
        cmd += " | python3 " + CLANG_TIDY_DIFF + " -p1"
        cmd += " -clang-tidy-binary " + CLANG_TIDY
        cmd += " -path " + BUILD_PATH + " -quiet"
        os.system(cmd)
    else:
        # This is a new added file since base revision
        cmd = "python3 " + RUN_CLANG_TIDY + " -clang-tidy-binary " + CLANG_TIDY
        cmd += " -clang-apply-replacements-binary " + CLANG_APPLY_REPLACEMENTS
        cmd += " -p " + BUILD_PATH + " -quiet " + arg
        os.system(cmd)


def main():
    if len(sys.argv) < 2:
        print("Usage: ./lint.py file [file ...]")
        sys.exit(0)
    executor = ThreadPoolExecutor(max_workers=16)
    files = sys.argv[1:]
    all_task = [executor.submit(clang_tidy_file, file) for file in files]
    wait(all_task, return_when=ALL_COMPLETED)


if __name__ == '__main__':
    main()
