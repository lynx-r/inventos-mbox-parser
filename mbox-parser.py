#! /usr/bin/env python3
import argparse
import getopt
from itertools import product
import re
import sys


def usage():
    print('cat message.mbox | mbox-parser.py -a aliases.txt')


def _has_alias(email, aliases):
    for alias_line in aliases:
        alias_list = alias_line.split(' ')
        if email in alias_list:
            return True, alias_list[0]
    return False, email


def parse_mbox_from_stdin(aliases):
    lines = sys.stdin.readlines()
    name_and_email_dict = {}
    for line in lines:
        if line.startswith('From:'):
            name_match = re.search('(?<=From: )[a-zA-Z ]+(?!\S)', line)
            email_match = re.search('<(.*?)>', line)
            if email_match:
                name = name_match.group(0) if name_match else ''
                email = email_match.group(1)
                if not aliases:
                    if email in name_and_email_dict:
                        count = name_and_email_dict[email][-1]
                        name_and_email_dict[email] = (name, email, count + 1)
                    else:
                        name_and_email_dict[email] = (name, email, 1)
                else:
                    has_alias = _has_alias(email, aliases)
                    if has_alias[0]:
                        key = has_alias[1]
                        if key in name_and_email_dict:
                            count = name_and_email_dict[key][-1]
                            name_and_email_dict[key] = (name, email, count + 1)
                        else:
                            name_and_email_dict[key] = (name, email, 1)
                    elif email in name_and_email_dict:
                        count = name_and_email_dict[email][-1]
                        name_and_email_dict[email] = (name, email, count + 1)
                    else:
                        name_and_email_dict[email] = (name, email, 1)
            else:
                print("Missed email in line: " + line)
                sys.exit(1)

    name_and_email_dict_sorted = sorted(name_and_email_dict.items(), key=lambda e: e[1][-1])

    for (k, v) in name_and_email_dict_sorted:
        print(k + ':', v[-1])


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--aliases', help='Псевдонимы пользователей')
    args = parser.parse_args()
    aliases = []
    if args.aliases:
        aliases = [line.rstrip() for line in open(args.aliases)]
    parse_mbox_from_stdin(aliases)


if __name__ == "__main__":
    main()
