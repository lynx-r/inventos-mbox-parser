import argparse
import getopt
import re
import sys


def usage():
    print('cat message.mbox | mbox-parser.py -a aliases.txt')


def parse_mbox_from_stdin(aliases):
    lines = sys.stdin.readlines()
    name_and_email_dict = {}
    not_use_aliases = not aliases
    for line in lines:
        if line.startswith('From:'):
            name_match = re.search('(?<=From: )[a-zA-Z ]+(?!\S)', line)
            email_match = re.search('<(.*?)>', line)
            if email_match:
                name = name_match.group(0) if name_match else ''
                email = email_match.group(1)
                if not_use_aliases:
                    if email in name_and_email_dict:
                        count = name_and_email_dict[email][-1]
                        name_and_email_dict[email] = (name, email, count + 1)
                    else:
                        name_and_email_dict[email] = (name, email, 1)
                else:
                    has_alias = [name == alias.split(' ')[0] or email == alias.split(' ')[0] for alias in aliases]
                    if has_alias[0] or has_alias[1]:
                        count = 0
                        key = ''
                        if has_alias[0] and name in name_and_email_dict:
                            count = name_and_email_dict[name][-1]
                            key = name
                        elif has_alias[1] and email in name_and_email_dict:
                            count = name_and_email_dict[email][-1]
                            key = email
                        elif has_alias[0]:
                            name_and_email_dict[name] = (name, email, 1)
                            continue
                        elif has_alias[1]:
                            name_and_email_dict[email] = (name, email, 1)
                            continue
                        name_and_email_dict[key] = (name, email, count + 1)
                    elif email in name_and_email_dict:
                        count = name_and_email_dict[email][-1]
                        name_and_email_dict[email] = (name, email, count + 1)
                    else:
                        name_and_email_dict[email] = (name, email, 1)
            else:
                print("Missed email")
                sys.exit(1)

    name_and_email_dict_sorted = sorted(name_and_email_dict.items(), key=lambda e: e[1][2])

    for (k, v) in name_and_email_dict_sorted:
        print(k, v[-1])


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