#! /usr/bin/python3

########################################################################
#                                                                      #
#   Cyprium is a multifunction cryptographic, steganographic and       #
#   cryptanalysis tool developped by members of The Hackademy.         #
#   French White Hat Hackers Community!                                #
#   www.thehackademy.fr                                                #
#   Copyright © 2012                                                   #
#   Authors: SAKAROV, Madhatter, mont29, Luxerails, PauseKawa, fred,   #
#   afranck64, Tyrtamos.                                               #
#   Contact: cyprium@thehackademy.fr, sakarov@thehackademy.fr,         #
#   madhatter@thehackademy.fr, mont29@thehackademy.fr,                 #
#   irc.thehackademy.fr #cyprium, irc.thehackademy.fr #hackademy       #
#                                                                      #
#   Cyprium is free software: you can redistribute it and/or modify    #
#   it under the terms of the GNU General Public License as published  #
#   by the Free Software Foundation, either version 3 of the License,  #
#   or any later version.                                              #
#                                                                      #
#   This program is distributed in the hope that it will be useful,    #
#   but without any warranty; without even the implied warranty of     #
#   merchantability or fitness for a particular purpose. See the       #
#   GNU General Public License for more details.                       #
#                                                                      #
#   The terms of the GNU General Public License is detailed in the     #
#   COPYING attached file. If not, see : http://www.gnu.org/licenses   #
#                                                                      #
########################################################################


import sys
import os
import string

# In case we directly run that file, we need to add the kernel to path,
# to get access to generic stuff in kernel.utils!
if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 "..", "..", "..")))

import kernel.utils as utils

__version__ = "0.5.0"
__date__ = "2012/01/10"
__python__ = "3.x"  # Required Python version
__about__ = "" \
"""===== About Biliteral =====

Biliteral is a cryptographic tool which can cypher text in the biliteral code,
which is a binary encoding using A and B as digits.

Cypher input can be any string containing ASCII lowercase letters only
(no spaces), decypher input must be an integer number of groups of five
(A,B) digits.

Note that [ij] and [uv] have the same biliteral codes.

Cyprium.Biliteral version {} ({}).
Licence GPL3
Software distributed on the site: http://thehackademy.fr

Current execution context:
    Operating System: {}
    Python version: {}
""".format(__version__, __date__, utils.__pf__, utils.__pytver__)


MAP = {k: utils.num_to_base(v, ('A', 'B'), 5)
                           for v, k in enumerate(string.ascii_lowercase)
                                    if k not in 'jv'}
MAP['j'] = MAP['i']
MAP['v'] = MAP['u']

R_MAP = utils.revert_dict(MAP, exceptions={MAP['i']: '[ij]', MAP['u']: '[uv]'})


def do_cypher(text):
    """
    Cypher message to triliteral (with optional base, shift)
    'd' --> AAABB
    """
    return "".join((MAP[c] for c in text))


def cypher(text):
    """Just a wrapper around do_cypher, with some checks."""
    if not text:
        raise ValueError("No text given!")
    # Check for unallowed chars…
    c_text = set(text)
    c_allowed = set(string.ascii_lowercase)
    if not (c_text <= c_allowed):
        raise ValueError("Text contains unallowed chars (only lowercase "
                         "strict ASCII chars are allowed): '{}'!"
                         "".format("', '".join(sorted(c_text - c_allowed))))
    return do_cypher(text)


def do_decypher(text):
    """
    Decypher message to triliteral (with optional base, shift)
    AAABB --> 'd'
    """
    return "".join((R_MAP[c] for c in utils.grouper2(text, 5)))


def decypher(text):
    """Just a wrapper around do_decypher, with some checks."""
    if not text:
        raise ValueError("No text given!")
    # Check for unallowed chars…
    c_text = set(text)
    c_allowed = {'A', 'B'}
    if not (c_text <= c_allowed):
        raise ValueError("Text contains unallowed chars (only A and B "
                         "are allowed): '{}'!"
                         "".format("', '".join(sorted(c_text - c_allowed))))
    # Check for length.
    if len(text) % 5:
        raise ValueError("Text must contains an integer number of groups of "
                         "five chars (current length: {})…"
                         "".format(len(text)))
    # Check for valid triliteral codes.
    c_text = {c for c in utils.grouper2(text, 5)}
    c_allowed = set(R_MAP.keys())
    if not (c_text <= c_allowed):
        raise ValueError("Text contains invalid biliteral codes: '{}'!"
                         "".format("', '".join(sorted(c_text - c_allowed))))
    return do_decypher(text)


def test():
    print("Start test...")
    txt = "".join(list(MAP.keys()) * 10)
    coded = cypher(txt)
    decoded = decypher(coded)
    if txt != decoded:
        raise Exception("Test error, text and decoded(coded) text are "
                        "not the same!")
    print("...Success")


def main():
    # The argparse is much nicer than directly using sys.argv...
    # Try 'program.py -h' to see! ;)
    import argparse
    parser = argparse.ArgumentParser(description=""
                                     "Cypher/decypher some lowercase-"
                                     "no-space text to/from biliteral"
                                     "code.")
    parser.add_argument('--debug', action="store_true", default=False,
                        help="Enable debug mode.")

    sparsers = parser.add_subparsers(dest="command")

    cypher_parser = sparsers.add_parser('cypher', help="Cypher text in "
                                                       "biliteral.")
    cypher_parser.add_argument('-i', '--ifile', type=argparse.FileType('r'),
                               help="A file containing the text to convert to "
                                    "biliteral.")
    cypher_parser.add_argument('-o', '--ofile', type=argparse.FileType('w'),
                               help="A file into which write the biliteral "
                                    "text.")
    cypher_parser.add_argument('-d', '--data',
                               help="The text to cypher in biliteral.")

    uncypher_parser = sparsers.add_parser('decypher',
                                          help="Decypher biliteral to text.")
    uncypher_parser.add_argument('-i', '--ifile', type=argparse.FileType('r'),
                                 help="A file containing the text to convert "
                                      "from biliteral.")
    uncypher_parser.add_argument('-o', '--ofile', type=argparse.FileType('w'),
                                 help="A file into which write the decyphered "
                                      "text.")
    uncypher_parser.add_argument('-d', '--data',
                                 help="The text to decypher.")

    sparsers.add_parser('about', help="About Biliteral…")

    args = parser.parse_args()
    utils.DEBUG = args.debug

    if args.command == "cypher":
        try:
            data = args.data
            if args.ifile:
                data = args.ifile.read()
            out = cypher(data)
            if args.ofile:
                args.ofile.write(out)
            else:
                print(out)
        except Exception as e:
            if utils.DEBUG:
                raise e
            print(e, "\n\n")
        finally:
            if args.ifile:
                args.ifile.close()
            if args.ofile:
                args.ofile.close()
        return 0

    elif args.command == "decypher":
        try:
            data = args.data
            if args.ifile:
                data = args.ifile.read()
            out = decypher(data)
            if args.ofile:
                args.ofile.write(out)
            else:
                print(out)
        except Exception as e:
            if utils.DEBUG:
                raise e
            print(e, "\n\n")
        finally:
            if args.ifile:
                args.ifile.close()
            if args.ofile:
                args.ofile.close()
        return 0

    elif args.command == "about":
        print(__about__)
        return


if __name__ == "__main__":
    main()
