# COMP6841 - Steganography Project

from PIL import Image
from Helpers import *
import os
import math

ENCODE = "1"
DECODE = "2"
RETURNMAIN = "return"
EXTPNG = ".png"

BYTETOKILOBYTE = 1/1000
BITTOBYTE = 1/8
RGBCHANNELS = 3
BYTETOBIT = 8

CONFIRM = "yes"
CONFIRM2 = "y"
DENY = "no"
DENY2 = "n"

# Note to self, the plaintext is "steganography"
DEFAULTHASH = "bfabba369a999a083b44f26c2da7bc52846cf39a872816d06969d2837840de6b"

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

    print('\nWould you like to encode data on this photo, type either "yes" or "no"')
    encodingConfirmation = input("Option Selected: ").lower()

    if encodingConfirmation == CONFIRM or encodingConfirmation == CONFIRM2:
        encodingFingerprint(fileDirectory)
    elif encodingConfirmation == DENY or encodingConfirmation == DENY2:
        clearTerminal()
        print("Returning to encoding menu\n")
        encodeMenu()
    else:
        clearTerminal()
        print("Please type a valid option\n")
        encodingSettings(fileDirectory)

def encodingFingerprint(fileDirectory):
    hash = DEFAULTHASH
    fileName = os.path.basename(fileDirectory)

    print('\nWould you like to use a specific fingerprint to identify ', fileName, 'type either "yes" or "no"')
    fingerprintChoice = input("Option Selected: ").lower()
    if fingerprintChoice == CONFIRM or fingerprintChoice == CONFIRM2:
        fingerprint = input('Fingerprint: ')
        hash = hashGenerator(fingerprint)
    elif fingerprintChoice != DENY and fingerprintChoice != DENY2:
        encodingFingerprint(fileDirectory)

    clearTerminal()
    print("Fingerprint has been created:", hash)
    encodingInformation(fileDirectory, hash)

def encodingInformation(fileDirectory, hash):
    info = input("Enter information to encode:")
    encodedData = dataEncoder(info, hash)
    totalBits = len(encodedData)
    totalPixels = math.ceil(totalBits / 3)

    print("totalPixels:", totalPixels, "totalBits:", totalBits, "\n")

    im = Image.open(fileDirectory)
    img = im.load()
    width, height = im.size

    for i in range(totalPixels):
        currentX = i % width
        currentY = math.floor(i / width)

        print("\nInfo -", img[currentX, currentY])

        for j in range(RGBCHANNELS):
            bitIndex = i * 3 + j
            if bitIndex >= totalBits:
                break

            print(f"Pixel ({currentX}, {currentY}) - BitIndex {bitIndex} | LSB {encodedData[bitIndex]}")

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