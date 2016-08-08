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


import sys
import os

# In case we directly run that file, we need to add the whole cyprium to path,
# to get access to CLI stuff!
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 "..", "..", "..", "..",
                                                 "..")))

import app.cli
import kernel.crypto.text.vigenere as vigenere
import kernel.utils as utils


class Vigenere(app.cli.Tool):
    """CLI wrapper for vigenere crypto text tool."""
    def main(self, ui):
        ui.message("********** Welcome to Cyprium.Vigenere! **********")
        quit = False
        while not quit:
            options = [(self.about, "*about", "Show some help!"),
                       (self.demo, "*demo", "Show some examples"),
                       (self.cypher, "*cypher",
                                     "Cypher some text in Vigenere"),
                       (self.decypher, "d*ecypher",
                                       "Decypher Vigenere into text"),
                       ("", "-----", ""),
                       ("tree", "*tree", "Show the whole tree"),
                       ("quit", "*quit", "Quit Cyprium.Vigenere")]
            msg = "Cyprium.Vigenere"
            answ = ui.get_choice(msg, options)

            if answ == 'tree':
                self._tree.print_tree(ui, self._tree.FULL)
            elif answ == 'quit':
                self._tree.current = self._tree.current.parent
                quit = True
            else:
                answ(ui)
        ui.message("Back to Cyprium menus! Bye.")

    def about(self, ui):
        ui.message(vigenere.__about__)
        ui.get_choice("", [("", "Go back to $menu", "")], oneline=True)

    def demo(self, ui):
        ui.message("===== Demo Mode =====")
        ui.message("Running a small demo/testing!")
        ui.message("--- Cyphering ---")

        keys = ["HACK", "HACK", "1024", "HACK"]
        algo_names = ["vigenere", "autoclave", "gronsfeld", "beaufort"]
        algos = [vigenere.ALGO_VIGENERE, vigenere.ALGO_AUTOCLAVE,
                 vigenere.ALGO_GRONSFELD, vigenere.ALGO_BEAUFORT]
        plain_text = "HELLO WORLD 1024"
        ui.message("plain-text  <->  key  <->  algorithm")
        for index, algo in enumerate(algos):
            ui.message(plain_text + " - " + keys[index] + " - " +
                       algo_names[index])
            ui.message("\t" + vigenere.cypher(plain_text, keys[index], algo))
        #ui.message("--- Decyphering ---")

        ui.message("Won't work!")
        try:
            plain_text = "HELLO WORLD"
            key = "1234"
            ui.message("plain-text  <->  key  <-> algorithm")
            ui.message(plain_text + "  <->  " + key + "  <->  vigenere")
            vigenere.cypher(plain_text, key, vigenere.ALGO_VIGENERE)
        except Exception as e:
            ui.message(str(e), level=ui.ERROR)
        ui.message("")

        ui.get_choice("", [("", "Go back to $menu", "")], oneline=True)

    def cypher(self, ui):
        """Interactive version of cypher()."""
        txt = ""
        ui.message("===== Cypher Mode =====")

        while 1:
            done = False
            while 1:
                txt = ui.text_input("Please input text to cypher",
                                    sub_type=ui.STRING)
                if txt is None:
                    break  # Go back to main Cypher menu.

                txt = txt.upper()

                # Get algo.

                options = [(vigenere.ALGO_VIGENERE, "$vigenere", ""),
                           (vigenere.ALGO_BEAUFORT, "*beaufort", ""),
                           (vigenere.ALGO_GRONSFELD, "*gronsfeld", ""),
                           (vigenere.ALGO_AUTOCLAVE, "auto*clave", "")]
                algo = ui.get_choice("Algorithm to use ", options)

                # Get key
                key = ui.get_data("Enter the key : ", sub_type=ui.STRING)
                key = key.upper()

                spaces = ui.get_choice("Conserve spaces ?", options=[
                        (True, "$yes", ""), (False, "*no", "")],
                        oneline=True)

                try:
                    txt = vigenere.cypher(txt, key, algo, spaces)
                    done = True  # Out of those loops, output result.
                    break
                except Exception as e:
                    if utils.DEBUG:
                        import traceback
                        traceback.print_tb(sys.exc_info()[2])
                    ui.message(str(e), level=ui.ERROR)
                    options = [("retry", "*try again", ""),
                               ("menu", "or go back to *menu", "")]
                    answ = ui.get_choice("Could not convert that data into "
                                         "Vigenere, please", options,
                                         oneline=True)
                    if answ in {None, "menu"}:
                        return  # Go back to main Sema menu.
                    # Else, retry with another data to hide.

            if done:
                ui.text_output("Text successfully converted", txt,
                               "cyphered-text")

            options = [("redo", "*cypher another text", ""),
                       ("quit", "or go back to $menu", "")]
            answ = ui.get_choice("Do you want to", options, oneline=True)
            if answ in {None, "quit"}:
                return

    def decypher(self, ui):
        """Interactive version of decypher and hack."""
        txt = ""
        ui.message("===== Decypher/Hack Mode =====")

        while 1:
            txt = ui.text_input("Please input the cyphered text ",
                                sub_type=ui.STRING)
            if txt is None:
                break

            txt = txt.upper()

            # Get algo.

            options = [(vigenere.ALGO_VIGENERE, "$vigenere", ""),
                       (vigenere.ALGO_BEAUFORT, "*beaufort", ""),
                       (vigenere.ALGO_GRONSFELD, "*gronsfeld", ""),
                       (vigenere.ALGO_AUTOCLAVE, "auto*clave", "")
                       ]
            algo = ui.get_choice("Algorithm to use", options)

            # Get key
            options = [(1, "*1 the key", ""),
                       (2, "*2 the key length and the language", ""),
                       (3, "*3 the key length", ""),
                       (4, "*4 the language", ""),
                       (5, "$5 have no clue", ""),]
            if algo==vigenere.ALGO_AUTOCLAVE:
                options = [(1, "$1 the key", "")]
            mode = ui.get_choice("You know... ", options)
            language = key_length = key = None
            if mode == 1:
                key = ui.get_data("Enter the key : ", sub_type=ui.STRING)
                key = key.upper()
            if mode in (2, 4):
                languages = vigenere.LANGUAGES
                options = []
                for i, lang in enumerate(languages):
                    if lang=="fr":
                        option = (lang, "$%d %s" % (i+1, languages[lang]), "")
                    else:
                        option = (lang, "*%d %s" % (i+1, languages[lang]), "")
                    options.append(option)
                language = ui.get_choice("The language is", options)
            if mode in (2, 3):
                key_length = ui.get_data("The key's length is ",
                        sub_type=ui.INT)
            if mode > 1:
                key = vigenere.hack(txt, algo, key_length, language)
            try:
                ui.text_output("Text successfully decyphered",
                               vigenere.decypher(txt, key, algo),
                               "")
            except Exception as e:
                if utils.DEBUG:
                    import traceback
                    traceback.print_tb(sys.exc_info()[2])
                ui.message(str(e), level=ui.ERROR)

            options = [("redo", "*decypher another data", ""),
                       ("quit", "or go back to $menu", "")]
            answ = ui.get_choice("Do you want to", options, oneline=True)
            if answ == "quit":
                return


NAME = "vigenere"
TIP = "Tool to convert text to/from Vigenere code."
TYPE = app.cli.Node.TOOL
CLASS = Vigenere

# Allow tool to be used directly, without using Cyprium menu.
if __name__ == "__main__":
    import app.cli.ui
    ui = app.cli.ui.UI()
    tree = app.cli.NoTree("vigenere")
    Vigenere(tree).main(ui)
