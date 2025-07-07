# COMP6841 - Steganography Project

from PIL import Image
from Helpers import *
import os

ENCODE = "1"
DECODE = "2"
RETURNMAIN = "return"
EXTPNG = ".png"

BYTETOKILOBYTE = 1/1024
BITTOBYTE = 1/8
RGBCHANNELS = 3

print("COMP6841 Steganography Project 1.0\n")

def mainMenu():
    print("Main Menu\n")
    print("|Options|")
    print("| 1 - Encode information |")
    print("| 2 - Decode information |")

    encodeOrDecode = input("Option selected: ")
    if encodeOrDecode == ENCODE:
        clearTerminal()
        encodeMenu()
    elif encodeOrDecode == DECODE:
        clearTerminal()
        decodeMenu()
    else:
        clearTerminal()
        print("Please select either option 1 or 2\n")
        mainMenu()

def encodeMenu():
    print("Encode menu (WiP)\n")
    print("|Options|")
    print("| Select encoding file: Type the full path of the file, including its name and extension.    |")
    print('| Return to menu: Type in "return" to return to the main menu.                               |')

    encodeSelection = input("Option selected: ")
    if encodeSelection.lower() == RETURNMAIN:
        clearTerminal()
        print("Returned to main menu\n")
        mainMenu()

    if os.path.isfile(encodeSelection):
        clearTerminal()
        print("Success - File exist!\n")
        encodingSettings(encodeSelection)
    else:
        clearTerminal()
        print("File does not exist!\n")
        encodeMenu()

def encodingSettings(fileDirectory):
    size = os.path.getsize(fileDirectory) * BYTETOKILOBYTE
    fileName = os.path.basename(fileDirectory)
    extension = os.path.splitext(fileDirectory)[1]

    print("File stats\n")
    print("Full file directory:", fileDirectory)
    print("File name:", fileName)
    print("File size:", size, "kB")
    print("File extension:", extension)

    if extension == EXTPNG:
        im = Image.open(fileDirectory)
        width, height = im.size
        encodeLimit = width * height * RGBCHANNELS * BITTOBYTE * BYTETOKILOBYTE

        print("\nDimensions:", width, "x", height)
        print("Encodable Information:", encodeLimit, "kB")

    input("Press Enter to exit...")


def decodeMenu():
    print("Decode menu (WiP)\n")
    print("| Decode file: Type the full path of the file, including its name and extension. |")
    print('| Return to menu: Type in "return" to return to the main menu.                   |')

    decodeSelection = input("Option selected: ")
    if decodeSelection.lower() == RETURNMAIN:
        clearTerminal()
        print("Returned to main menu\n")
        mainMenu()

    if os.path.isfile(decodeSelection):
        print("Success - File exist!\n")
    else:
        clearTerminal()
        print("File does not exist!\n")
        decodeMenu()

    input("Press Enter to exit...")

mainMenu()