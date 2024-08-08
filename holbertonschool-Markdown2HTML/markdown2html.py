#!/usr/bin/python3
"""
This program will read a markdown file and convert it to HTML
"""

from typing import Any, List, Match
from sys import argv
from os import access, R_OK, F_OK
import re
import hashlib


def eprint(*args: str, **kwargs: Any) -> None:
    """
    Print in the standar error

    @args: Message to print
    @kwargs: optional arguments for print function
    Returns: None
    """
    from sys import stderr
    print(*args, file=stderr, **kwargs)


def program_error(msg: str) -> None:
    """
    Exit program with 1, when ocurrs an error and
    print a message on the stderr.

    @msg: Message to print
    Returns: None
    """
    eprint(msg)
    exit(1)


def validate_heading(string: str) -> None:
    """
    Reads a string and validate if is a heading from markdown format

    Args:
        string (str): String to validate
    """
    result = re.search(r"(^#{1,6}) (.*)", string)
    if (result):
        groups = result.groups()
        hashes: int = len(groups[0])
        text: str = groups[1]
        # print(f"<h{hashes}>{text}</h{hashes}>")
        to_write.append(f"<h{hashes}>{text}</h{hashes}>\n")


def validate_unordered_list(words: List[str], idx: int,
                            total_words: int) -> None:
    """
    Reads a string and validate if is a unordered list from markdown format

    Args:
        words (List[str]): List of words
        idx (int): Position of the word to validate
        words (int): Quantity of words
    """

    regex = r"^- (.*)"

    before_line = re.search(regex, words[idx - 1])
    current_line = re.search(regex, words[idx])
    after_line = re.search(
        regex, words[idx + 1] if idx + 1 < total_words else '')

    if (not before_line):
        # print("<ul>")
        to_write.append("<ul>\n")

    if current_line:
        text: str = current_line.groups()[0]
        # print(f"\t<li>{text}</li>")
        to_write.append(f"\t<li>{text}</li>\n")

    if (not after_line):
        # print("</ul>")
        to_write.append("</ul>\n")


def validate_ordered_list(words: List[str], idx: int,
                          total_words: int) -> None:
    """
    Reads a string and validate if is a ordered list from markdown format

    Args:
        words (List[str]): List of words
        idx (int): Position of the word to validate
        total_words (int): Quantity of words
    """

    regex = r"^\* (.*)"

    before_line = re.search(regex, words[idx - 1])
    current_line = re.search(regex, words[idx])
    after_line = re.search(
        regex, words[idx + 1] if idx + 1 < total_words else '')

    if (not before_line):
        # print("<ol>")
        to_write.append("<ol>\n")

    if current_line:
        text = current_line.groups()[0]
        # print(f"\t<li>{text}</li>")
        to_write.append(f"\t<li>{text}</li>\n")

    if (not after_line):
        # print("</ol>")
        to_write.append("</ol>\n")


def print_simple_text(words: List[str], idx: int, total_words: int) -> None:
    """
    Reads a string and validate if is a simple text from markdown format

    Args:
        words (List[str]): List of words
        idx (int): Position of the word to validate
        total_words (int): Quantity of words
    """

    regex = r"^[^-# \n].*"

    before_line = re.search(regex, words[idx - 1])
    current_line = re.search(regex, words[idx])
    following_word = re.search(
        regex, words[idx + 1] if idx + 1 < total_words else '')

    if (current_line):
        if (not before_line):
            # print("<p>")
            to_write.append("<p>\n")

        text = current_line.group()
        # print(text)
        to_write.append(f"{text}\n")

        # print("<br/>" if following_word else "</p>")
        to_write.append("<br/>\n" if following_word else "</p>\n")


def convert_to_bold_b(match_obj: Match) -> str:
    """Takes a words and converts them to a bold string

    Args:
        match_obj (Match): A word arround "**"
        founded by regex matching

    Returns:
        to_convert (str): Returns the converted string in a bold style format.
    """
    to_convert = match_obj.group()

    if (to_convert[0] == '*'):
        to_convert = f"<b>{to_convert[2:-2]}</b>"

    return (to_convert)

def convert_to_bold_em(match_obj: Match) -> str:
    """Takes a words and converts them to a bold string

    Args:
        match_obj (Match): A word arround "__"
        founded by regex matching

    Returns:
        to_convert (str): Returns the converted string in a bold style format.
    """
    to_convert = match_obj.group()

    if (to_convert[0] == '_'):
        to_convert = f"<em>{to_convert[2:-2]}</em>"

    return (to_convert)


def convert_to_md5(match_obj) -> str:
    """Takes a words and converts them to md5 hash

    Args:
        match_obj (Match): A word arround "[[]]" founded by regex matching

    Returns:
        md5_str (str): Returns an md5 hash in hexadecimal.
    """
    to_convert = match_obj.groups()[0].encode()

    return (hashlib.md5(to_convert).hexdigest())


def remove_c_character(match_obj) -> str:
    """Takes a words and remove the c characters

    Args:
        match_obj (Match): A word arround "(())" founded by regex matching

    Returns:
        to_convert (str): Returns a string without 'c' and 'C'.
    """
    to_convert = match_obj.groups()[0]
    to_convert = to_convert.replace("c", "").replace("C", "")

    return (to_convert)

if (__name__ == '__main__'):
    argc: int = len(argv)

    if (argc < 3):
        program_error("Usage: ./markdown2html.py README.md README.html")

    markdown_name_file: str = argv[1]
    output_name_file: str = argv[2]
    to_write: List[str] = []

    if (not access(markdown_name_file, F_OK)):
        program_error(f"Missing {markdown_name_file:s}")

    if (not access(markdown_name_file, R_OK)):
        program_error(
            f"You don't have the right permissions to read '{markdown_name_file}'")


    with open(markdown_name_file, 'r') as _file:
        lines = _file.readlines()
        quantity_of_lines: int = len(lines)

        for i in range(0, quantity_of_lines):
            lines[i] = re.sub(r"\(\(([\w /]+)\)\)", remove_c_character, lines[i])
            lines[i] = re.sub(r"\[\[([\w /]+)\]\]", convert_to_md5, lines[i])
            lines[i] = re.sub(r"(\*\*[\w <>/]+\*\*)", convert_to_bold_b, lines[i])
            lines[i] = re.sub(r"(__[\w <>/]+__)", convert_to_bold_em, lines[i])

            if (lines[i][0] == '#'):
                validate_heading(lines[i])
            elif (lines[i][0] == '-'):
                validate_unordered_list(lines, i, quantity_of_lines)
            elif (lines[i][0] == '*'):
                validate_ordered_list(lines, i, quantity_of_lines)
            else:
                print_simple_text(lines, i, quantity_of_lines)

    with open(output_name_file, 'w') as _file:
        _file.writelines(to_write)

    exit(0)
