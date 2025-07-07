# COMP6841 - Steganography Project Helpers File

import os

def clearTerminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')