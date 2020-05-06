"""
FILE:
    diff_tool.py
    
VERSION:
    .1 - initial file with arguments
    .2 - adding HTML output
    .3 - removing delta variable to hand out results directly to output file
         or to stdout.
    
DESCRIPTION:
    script that shows the difference between two files.
    
    https://florian-dahlitz.de/blog/create-your-own-diff-tool-using-python
"""

import difflib
import sys
import argparse

from pathlib import Path
from typing import Union, Iterator


def create_diff(old_file: Path, new_file: Path, output_file: Path=None) -> None:
    file_1 = open(old_file).readlines()
    file_2 = open(new_file).readlines()

    if output_file:
        with open(output_file, "w") as f:
            f.write(difflib.HtmlDiff().make_file(
                file_1, file_2, old_file.name, new_file.name
                )
            )
            f.close()
    else:
        sys.stdout.writelines(difflib.unified_diff(
            file_1, file_2, old_file.name, new_file.name)
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("old_file_version")
    parser.add_argument("new_file_version")
    parser.add_argument("--html", help="specify html to write to")
    args = parser.parse_args()
    
    old_file = Path(args.old_file_version)
    new_file = Path(args.new_file_version)
    
    if args.html:
        output_file = Path(args.html)
    else:
        output_file = None
    
    create_diff(old_file, new_file, output_file)
    

if __name__ == "__main__":
    main()
