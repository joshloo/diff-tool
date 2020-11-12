"""
FILE:
    diff_tool.py

DESCRIPTION:
    script that shows the difference between two files.

    https://florian-dahlitz.de/blog/create-your-own-diff-tool-using-python

    This code includes modification from original source to compare delta between debug
    log files to narrow down potential boot issues.

    As such, it is recommended to run the tool with commend sequence below.
    diff_tool pass.log fail.log
"""

import difflib
import sys
import argparse

from pathlib import Path
from typing import Union, Iterator

# This function predicts which component might go wrong after the diff.
# it takes in the whole diff string, and run through the component list
# and see which one match the most to come into a conclusion.
def deduce_component(diff_string, componentlist):
    if (diff_string == ''):
      print("\n nothing to diff")
      return
    if (componentlist == []):
      print("\n no component to deduce")
      return
    current_count = 0
    max_count = 0
    issue_component = ''
    for i in componentlist:
      current_count = diff_string.upper().count(i.upper())
      if (current_count > max_count):
        issue_component = i
        max_count = current_count
      print(i, " counts: ", current_count)
    if (issue_component == ''):
      print("\nUnable to deduce any issue in the list")
    else:
      print("\nDeduced issue component: ", issue_component)

# This function constructs the last n lines of diff string to create a more
# refined string. This is to eliminate the noise level of diff. Having a
# big n parameter will cause a lot to be dumped out and interpreted,
# which sometimes is not a good thing if we want to know which element hang
# at last part of fail log.
def construct_last_n_string(n, diff_string):
    if (n == 0):
      print("no lines to diff")
      return ''
    if (diff_string == ''):
      print("no string to diff")
      return ''
    nlines = diff_string.count('\n')
    if (n > nlines):
      print("nlines : ", nlines)
      print("out of bound. try running with lower n parameter less than nlines. eg: -n 1" )
      return ''
    # get the last few lines in the diff string
    targetted_diff = ''
    for i in range (n, 0, -1):
      targetted_diff = targetted_diff + diff_string.split('\n')[-i] + '\n'
    return targetted_diff

# This is the original implementation of creating a diff output.
# it will be either as an output filename, or in command prompt.
# for this POC, it will put more focus on command prompt.
def create_diff(old_file: Path, new_file: Path, output_file: Path=None, numlines = 5) -> None:
    file_1 = open(old_file).readlines()
    file_2 = open(new_file).readlines()

    if output_file:
        with open(output_file, "w") as f:
            f.write(difflib.HtmlDiff().make_file(
                file_1, file_2, old_file.name, new_file.name, True,5
                )
            )
            f.close()
    else:
        diff_object = difflib.unified_diff(
             file_1, file_2, old_file.name, new_file.name, "","",3)
        diff_string = ''.join(diff_object)

        # categories are defined here. Can be potentially changed to dictionary to point to owners per components.
        # yocto_components = ['tsn', 'audio']
        bios_components = ['com','usb', 'pci', 'shell', 'mrc', 'i2c', 'spi', 'tpm', 'xhci']
        
        print("---------------------------")
        print("Whole log diff report")
        print("---------------------------")
        deduce_component(diff_string, bios_components)

        print("---------------------------")
        print("Targetted log diff report")
        print("---------------------------")
        targetted_diff = construct_last_n_string(numlines, diff_string)
        print(targetted_diff)
        deduce_component(targetted_diff, bios_components)

def main():
    print("======================")
    print("Log analyzer diff tool")
    print("======================")
    parser = argparse.ArgumentParser()
    parser.add_argument("old_file_version")
    parser.add_argument("new_file_version")
    parser.add_argument("--html", help="specify html to write to")
    parser.add_argument("-n", "--numline",type=int, default=5, help="specify how many lines to diff", )
    args = parser.parse_args()
    
    old_file = Path(args.old_file_version)
    new_file = Path(args.new_file_version)
    numlines =  args.numline

    if args.html:
        output_file = Path(args.html)
    else:
        output_file = None
    
    create_diff(old_file, new_file, output_file, numlines)
    

if __name__ == "__main__":
    main()
