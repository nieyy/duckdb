#!/usr/bin/env python3
"""
Check C/C++ define comments.
1. #ifdef WITH_NIEYUANYUAN ->  #endif /* WITH_NIEYUANYUAN */
2. #ifndef WITH_NIEYUANYUAN -> #endif /* !WITH_NIEYUANYUAN */
"""

import sys
import re

MACRO_NAME = "WITH_NIEYUANYUAN"
IFDEF_PATTERN = re.compile(r'^#ifdef\s+WITH_NIEYUANYUAN\s*$')
IFNDEF_PATTERN = re.compile(r'^#ifndef\s+WITH_NIEYUANYUAN\s*$')
ENDIF_COMMENT_PATTERN = re.compile(r'^#endif\s+/\*\s*(!?WITH_NIEYUANYUAN)\s*\*/\s*$')


class MacroStack:
    def __init__(self):
        self.stack = []

    def push(self, is_ifdef):
        self.stack.append(('WITH_NIEYUANYUAN', is_ifdef))

    def pop(self):
        return self.stack.pop() if self.stack else None


def check_file(filename):
    """Check single file"""
    stack = MacroStack()
    errors = 0
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.strip()
                if IFDEF_PATTERN.match(clean_line):
                    stack.push(True)
                elif IFNDEF_PATTERN.match(clean_line):
                    stack.push(False)
                elif re.match(r'#\s*if', clean_line):
                    stack.push(None)
                elif re.match(r'#\s*endif', clean_line):
                    current = stack.pop()
                    if current[1] is None:
                        continue  # ignore other #endif

                    # check format
                    match = ENDIF_COMMENT_PATTERN.match(clean_line)
                    required_comment = 'WITH_NIEYUANYUAN' if current[1] else '!WITH_NIEYUANYUAN'
                    if not match or match.group(1) != required_comment:
                        print("{}:{} {} >>> #endif /* {} */".format(filename, line_num, clean_line, required_comment))
                        errors = errors + 1

    except Exception as e:
        print("Check {} failed: {} . Skipping...".format(filename, e))
    if errors > 0:
        return False
    return True


if __name__ == "__main__":
    error_files = []

    if len(sys.argv) < 2:
        print("Usage: python3 check_macro_comments.py file1 file2 ...")
        sys.exit(1)

    for filename in sys.argv[1:]:
        if not check_file(filename):
            error_files.append(filename)

    if error_files:
        sys.exit(1)
    else:
        sys.exit(0)
