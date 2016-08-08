#! /usr/bin/python3

########################################################################
#                                                                      #
#   Cyprium is a multifunction cryptographic, steganographic and       #
#   cryptanalysis tool developped by members of The Hackademy.         #
#   French White Hat Hackers Community!                                #
#   cyprium.hackademics.fr                                             #                                                  #
#   Authors: SAKAROV, mont29, afranck64                                #
#   Contact: admin@hackademics.fr                                      #
#   Forum: hackademics.fr                                              #
#   Twitter: @hackademics_                                             #
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

# PEP8

import app
import app.cli
import app.cli.ui
import app.cli.root
import kernel.utils as utils


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=""
                                     "Cyprium: main app regrouping many "
                                     "cryptographic/steganographic tools, "
                                     "as well as some cryptanalysis ones.")
    parser.add_argument('-d', '--debug', action="store_true", default=False,
                        help="Enable debug mode.")

    args = parser.parse_args()
    utils.DEBUG = args.debug

    tree = app.cli.Tree(app.cli.root)

    ui = app.cli.ui.UI()

    tree.main(ui)
