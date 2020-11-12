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
from urllib.request import urlopen

from pathlib import Path
from typing import Union, Iterator

#defines
NO_BIOS_ID  = 'no BIOS id found'
NO_BOARD_ID = 'no board id found'

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


# This function gets the BIOS ID given a file read string list
def get_bios_id(stringlist):
    if (stringlist == []):
      return NO_BIOS_ID
    for line in stringlist:
      if "BIOS ID:" in line:
        return line.strip()
    return NO_BIOS_ID

# This function gets the board ID given a file read string list
def get_board_id(stringlist):
    if (stringlist == []):
      return NO_BOARD_ID
    for line in stringlist:
      if "BoardId is " in line:
        return line.strip()
    return NO_BOARD_ID

# This function gets the Yocto ID given file read string list
def get_yocto_id(stringlist):
    print('todo')

# This function gets file from URL, if the pass log will be in CI
def get_file_from_url(url):
    for line in urlopen(url):
      print(line)

# This is the original implementation of creating a diff output.
# it will be either as an output filename, or in command prompt.
# for this POC, it will put more focus on command prompt.
def create_diff(pass_file: Path, fail_file: Path, output_file: Path=None, numlines = 5) -> None:
    pass_file_list = open(pass_file).readlines()
    fail_file_list = open(fail_file).readlines()

    if output_file:
        with open(output_file, "w") as f:
            f.write(difflib.HtmlDiff().make_file(
                pass_file_list, fail_file_list, pass_file.name, fail_file.name, True,5
                )
            )
            f.close()
    else:
        diff_object = difflib.unified_diff(
             pass_file_list, fail_file_list, pass_file.name, fail_file.name, "","",3)
        diff_string = ''.join(diff_object)

        # categories are defined here. Can be potentially changed to dictionary to point to owners per components.
        # yocto_components = ['tsn', 'audio']
        bios_components = ['com','usb', 'pci', 'shell', 'mrc', 'i2c', 'spi', 'tpm', 'xhci']
        
        print("---------------------------")
        print("Whole log diff")
        print("---------------------------")
        deduce_component(diff_string, bios_components)

        print("---------------------------")
        print("Targetted log diff")
        print("---------------------------")
        targetted_diff = construct_last_n_string(numlines, diff_string)
        print(targetted_diff)
        deduce_component(targetted_diff, bios_components)

        print("---------------------------")
        print("Compare BIOS ID")
        print("---------------------------")
        print("pass case: ", get_bios_id(pass_file_list))
        print("fail case: ", get_bios_id(fail_file_list))
        if ((get_bios_id(pass_file_list) == get_bios_id(fail_file_list)) and
            get_bios_id(pass_file_list) != NO_BIOS_ID):
          print("Both BIOS ID identical")
        elif (get_bios_id(pass_file_list) == NO_BIOS_ID):
          print(NO_BIOS_ID)
        else:
          print("Different BIOS ID, please use right component, rejecting HSD..")

        print("---------------------------")
        print("Compare BOARD ID")
        print("---------------------------")
        print("pass case: ", get_board_id(pass_file_list))
        print("fail case: ", get_board_id(fail_file_list))
        if ((get_board_id(pass_file_list) == get_board_id(fail_file_list)) and
            get_board_id(pass_file_list) != NO_BOARD_ID):
          print("Both board ID identical")
        elif (get_board_id(pass_file_list) == NO_BOARD_ID):
          print(NO_BOARD_ID)
        else:
          print("Different Board ID, please use right component, rejecting HSD..")

        # print("---------------------------")
        # print("Get file from URL")
        # print("---------------------------")
        # get_file_from_url('http://www.sci.utah.edu/~macleod/docs/txt2html/sample.txt')

def main():
    print("======================")
    print("Log analyzer")
    print("======================")
    parser = argparse.ArgumentParser()
    parser.add_argument("pass_file_version")
    parser.add_argument("fail_file_version")
    parser.add_argument("--html", help="specify html to write to")
    parser.add_argument("-n", "--numline",type=int, default=5, help="specify how many lines to diff", )
    args = parser.parse_args()
    
    pass_file = Path(args.pass_file_version)
    fail_file = Path(args.fail_file_version)
    numlines =  args.numline

    if args.html:
        output_file = Path(args.html)
    else:
        output_file = None
    create_diff(pass_file, fail_file, output_file, numlines)

if __name__ == "__main__":
    main()
