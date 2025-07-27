# COMP6841 - Steganography Project

import os
import math
from PIL import Image
from Helpers import *
from pathlib import Path
from blake3 import blake3

ENCODE = "1"
DECODE = "2"
RETURNMAIN = "return"
QUITAPP = "quit"
QUITNUMBER = "3"
EXTPNG = ".png"

TEXTINPUT = "1"
FILEINPUT = "2"

BYTETOBIT = 8
BYTETOKILOBYTE = 1 / 1000
RGBCHANNELS = 3

CONFIRM = "yes"
CONFIRM2 = "y"
DENY = "no"
DENY2 = "n"

NULLBIT = "0"
POSBIT = "1"

VARWARNING = 500
ENTWARNING = 5

HASHSIZE = 64
HASHHALF = 32

EXTHEADER = "|EXT="
DEFAULTHEADER = "Text "

DEFAULTPASS = "steganography"
DEFAULTHASH = "bfabba369a999a083b44f26c2da7bc52846cf39a872816d06969d2837840de6b"

NOFILE = 1
INVALIDOPTION = 2
NOINFORMATION = 3
INVALIDMSG = 4

print("★ Stego Tools ★\n")


def mainMenu():
    printMainMenu()

    mainMenuOption = input("Option Selected: ")
    if mainMenuOption == ENCODE:
        clearTerminal()
        encodeMenu()
    elif mainMenuOption == DECODE:
        clearTerminal()
        decodeMenu()
    elif mainMenuOption == QUITNUMBER:
        displayExitMenu()
    else:
        clearTerminal()
        print("★ Choose either option 1 or option 2 to continue. ★\n")
        mainMenu()


def encodeMenu():
    printEncodingMenu()

    encodeSelection = input("Option Selected: ")
    if encodeSelection.lower() == RETURNMAIN:
        clearTerminal()
        print("★ Returning to Main Menu... ★\n")
        mainMenu()

    if os.path.isfile(encodeSelection):
        clearTerminal()
        print("★ Success - Provided File Exists! ★\n")
        encodingSettings(encodeSelection)
    else:
        clearTerminal()
        printError(NOFILE)
        encodeMenu()


def encodingSettings(filePath):
    fileSize = os.path.getsize(filePath) * BYTETOKILOBYTE
    fileName = os.path.basename(filePath)
    extension = os.path.splitext(filePath)[1]

    printFileStats(filePath, fileName, fileSize, extension)

    if extension != EXTPNG:
        print(
            f"\nPlease use a supported format, the {extension} format is currently not supported"
        )
        input("\nPress Enter to return to the encoding menu...")
        clearTerminal()
        print("★ Returning to encoding menu... ★\n")
        encodeMenu()

    printImageStats(filePath)
    printStegHeuristics(filePath)

    print("\n★ Do you want to embed data in this image? ★")
    encodingConfirmation = input('Enter "yes" or "no": ').lower()

    if encodingConfirmation == CONFIRM or encodingConfirmation == CONFIRM2:
        clearTerminal()
        print("★ Success — Proceeding to Fingerprinting Settings... ★\n")
        encodingFingerprint(filePath)
    elif encodingConfirmation == DENY or encodingConfirmation == DENY2:
        clearTerminal()
        print("★ Returning to encoding menu... ★\n")
        encodeMenu()
    else:
        clearTerminal()
        printError(INVALIDOPTION)
        encodingSettings(filePath)


def encodingFingerprint(filePath):
    fingerprint = DEFAULTPASS
    fileName = os.path.basename(filePath)

    print(f'★ Do you want to use a custom fingerprint to identify "{fileName}"? ★')
    fingerprintChoice = input('Enter "yes" or "no": ').lower()
    if fingerprintChoice == CONFIRM or fingerprintChoice == CONFIRM2:
        fingerprint = input("Enter Fingerprint: ")
        if fingerprint == "":
            fingerprint = DEFAULTPASS

    elif fingerprintChoice != DENY and fingerprintChoice != DENY2:
        clearTerminal()
        printError(INVALIDOPTION)
        encodingFingerprint(filePath)

    hash = hashGenerator(fingerprint)

    print(f"\n★ Fingerprint has been created: {hash} ★\n")

    input("Press Enter to Continue...")
    clearTerminal()

    print("★ Success — Proceeding to Encoding Settings... ★\n")
    encodingInformation(filePath, hash, fingerprint)


def encodingInformation(filePath, hash, fingerprint):
    if hash == DEFAULTHASH:
        print(
            "⚠ WARNING: Default fingerprint in use. This fingerprint is not secure ⚠\n"
        )

    encodingHeader = encodingSelection()
    encodedData = dataEncoder(encodingHeader, hash, fingerprint)
    totalBits = len(encodedData)

    im = Image.open(filePath)
    width, height = im.size
    encodeLimit = width * height * RGBCHANNELS
    if totalBits > encodeLimit:
        encodingErrorDisplay()
        encodingInformation(filePath, hash)

    totalPixels = math.ceil(totalBits / 3)

    printEncodingSettings(totalBits, totalPixels, hash)

    print("\n★ Please Enter a Name for the Output File (default: output.png) ★")
    outputName = input("Output Name: ")
    if outputName == "":
        scriptDir = os.path.dirname(os.path.abspath(__file__))
        outputName = scriptDir + r"\output.png"

    print("\n★ Would you like to proceed with encoding this message? ★")
    confirmation = input('Enter "yes" or "no": ').lower()
    if confirmation == DENY or confirmation == DENY2:
        clearTerminal()
        print("★ Returning to encoding menu... ★\n")
        encodeMenu()
    elif confirmation != CONFIRM and confirmation != CONFIRM2:
        clearTerminal()
        printError(INVALIDOPTION)
        encodingInformation(filePath, hash)

    img = im.load()

    mapping = generateSecureSample(fingerprint, encodeLimit, totalBits)

    for i in range(totalBits):
        currentPixel = math.ceil(mapping[i] / 3)
        xCoords = currentPixel % width
        yCoords = math.floor(currentPixel / width)
        currentChannel = mapping[i] % 3

        pixel = list(img[xCoords, yCoords])
        pixel[currentChannel] = (pixel[currentChannel] & ~1) | int(encodedData[i])
        # print(f"{i} - bit {mapping[i]} | pixel {currentPixel} [{xCoords}, {yCoords}] | channel [{currentChannel} - Val: {pixel[currentChannel] & 1}]")
        img[xCoords, yCoords] = tuple(pixel)

    im.save(outputName)
    print(
        f'\n★ Success — Information has been Successfully Embedded Into "{outputName}". ★'
    )

    print('\n★ Press Enter to return to the menu, or type "quit" to exit. ★')
    menuSelection = input("Option Selected: ").lower()
    if menuSelection == QUITAPP:
        displayExitMenu()

    clearTerminal()
    print("★ Returning to Main Menu... ★\n")
    mainMenu()


def decodeMenu():
    printDecodeMenu()

    decodeSelection = input("Option Selected: ")
    if decodeSelection.lower() == RETURNMAIN:
        clearTerminal()
        print("★ Returning to Main Menu... ★\n")
        mainMenu()

    if os.path.isfile(decodeSelection):
        clearTerminal()
        print("★ Success - Provided File Exists! ★\n")
        decodeInformationFootprint(decodeSelection)

    else:
        clearTerminal()
        printError(NOFILE)
        decodeMenu()

    input("Press Enter to exit...")
    clearTerminal()
    mainMenu()


def decodeInformationFootprint(filePath):
    print(
        "★ Please enter your fingerprint. If left blank, the default fingerprint 'steganography' will be used. ★\n"
    )
    hashPlainText = input("Please input your footprint: ")
    if hashPlainText == "":
        hashPlainText = "steganography"

    clearTerminal()
    print(f'★ Decoding data using fingerprint, "{hashPlainText}" ★')

    hash = hashGenerator(hashPlainText)
    firstHalf = slice(HASHHALF)
    lastHalf = slice(HASHHALF, HASHSIZE)
    firstFingerprint = hash[firstHalf]
    lastFingerprint = hash[lastHalf]

    im = Image.open(filePath)
    width, height = im.size
    totalBits = width * height * RGBCHANNELS

    lsbString = extractLSBBits(filePath, HASHHALF * BYTETOBIT, hashPlainText)
    asciiOutput = bitsToAscii(lsbString)

    if firstFingerprint in asciiOutput:
        print(
            f"\n★ Verification Successful — the Fingerprint '{hashPlainText}' is Correct. \n"
        )

        lsbString = extractLSBBits(filePath, totalBits - RGBCHANNELS, hashPlainText)
        asciiOutput = bitsToAscii(lsbString)

        if lastFingerprint in asciiOutput:
            startIndex = asciiOutput.find(firstFingerprint)
            endIndex = asciiOutput.find(lastFingerprint)

            print(
                f"\n★ Verification Successful — the Fingerprint '{hashPlainText}' is Correct. \n"
                )

            rawInformation = slice(startIndex + HASHHALF, endIndex)
            asciiOutput = decryptText(hashPlainText, asciiOutput[rawInformation])
        
            if (EXTHEADER + DEFAULTHEADER) in asciiOutput:
                printDecodedInformation(TEXTINPUT, asciiOutput)
            else:
                printDecodedInformation(FILEINPUT, asciiOutput)

        else:
            printError(NOINFORMATION)
    
    else:
        printError(NOINFORMATION)

    print('\n★ Press Enter to return to the menu, or type "quit" to exit. ★')
    menuSelection = input("Option Selected: ").lower()
    if menuSelection == QUITAPP:
        displayExitMenu()

    clearTerminal()
    print("★ Returning to Main Menu... ★\n")
    mainMenu()

mainMenu()