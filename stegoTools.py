# COMP6841 - Steganography Project

import math
import os

from PIL import Image

from DisplayScripts import *
from Helpers import *

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

HASHSIZE = 64
HASHHALF = 32

EXTHEADER = "|EXT="
TEXTHEADER = "Text "

DEFAULTPASS = "steganography"

NOFILE = 0
INVALIDOPTION = 1
NOINFORMATION = 2
INVALIDMSG = 3

print("★ Stego Tools ★\n")


def mainMenu():
    """
    Display the main menu and handle the user's selection.

    Params:
        None

    Returns:
        None
    """

    printMainMenu()

    menuOption = input("Option Selected: ")
    if menuOption == ENCODE:
        clearTerminal()
        encodeMenu()
    elif menuOption == DECODE:
        clearTerminal()
        decodeMenu()
    elif menuOption == QUITNUMBER:
        displayExitMenu()
    else:
        clearTerminal()
        print("★ Please type 1, 2 or 3 to continue. ★\n")
        mainMenu()


def encodeMenu():
    """
    Prompts the user to enter a file to encode information into as well
    as handling user inputs.

    Params:
        None

    Returns:
        None
    """

    printEncodingMenu()

    encodeOption = input("Option Selected: ")
    if encodeOption.lower() == RETURNMAIN:
        clearTerminal()
        print("★ Returning to Main Menu... ★\n")
        mainMenu()

    if os.path.isfile(encodeOption):
        clearTerminal()
        print("★ Success - Provided File Exists! ★\n")
        encodingSettings(encodeOption)
    else:
        clearTerminal()
        printError(NOFILE)
        encodeMenu()


def encodingSettings(filePath):
    """
    Analyze a given file and providing user with steganalysis information and
    prompts user regarding encoding options.

    Params:
        filePath (str): The path to the image file selected for encoding.

    Returns:
        None
    """

    fileSize = os.path.getsize(filePath) * BYTETOKILOBYTE
    fileName = os.path.basename(filePath)
    extension = os.path.splitext(filePath)[1]

    printFileStats(filePath, fileName, fileSize, extension)

    if extension != EXTPNG:
        print(
            f"\nPlease use the .png format, the {extension} format is currently not supported"
        )
        input("\nPress Enter to return to the encoding menu...")
        clearTerminal()
        print("★ Returning to encoding menu... ★\n")
        encodeMenu()

    printImageStats(filePath)
    printStegHeuristics(filePath)

    print("\n★ Do you want to embed data in this image? ★")
    confirmation = input('Enter "yes" or "no": ').lower()

    if confirmation == CONFIRM or confirmation == CONFIRM2:
        clearTerminal()
        print("★ Success — Proceeding to Fingerprinting Settings... ★\n")
        encodingFingerprint(filePath)
    elif confirmation == DENY or confirmation == DENY2:
        clearTerminal()
        print("★ Returning to encoding menu... ★\n")
        encodeMenu()
    else:
        clearTerminal()
        printError(INVALIDOPTION)
        encodingSettings(filePath)


def encodingFingerprint(filePath):
    """
    Prompts the user to create a fingerprint for the encoded file, if no
    fingerprint is entered, a custom fingerprint is used.

    Params:
        filePath (str): The path to the image file selected for encoding.

    Returns:
        None
    """

    fingerprint = DEFAULTPASS
    fileName = os.path.basename(filePath)

    print(f'★ Do you want to use a custom fingerprint to identify "{fileName}"? ★')
    customOption = input('Enter "yes" or "no": ').lower()
    if customOption == CONFIRM or customOption == CONFIRM2:
        fingerprint = input("Enter Fingerprint: ")
        if fingerprint == "":
            fingerprint = DEFAULTPASS

    elif customOption != DENY and customOption != DENY2:
        clearTerminal()
        printError(INVALIDOPTION)
        encodingFingerprint(filePath)

    hash = hashGenerator(fingerprint)

    print(f"\n★ Fingerprint has been created: {hash} ★\n")

    input("Press Enter to Continue...")
    clearTerminal()

    print("★ Success — Proceeding to Encoding Settings... ★\n")
    encodingInformation(filePath, hash, fingerprint)


def encodingInformation(filePath, hash, key):
    """
    Encodes, encrypts and embeds encoded data into the provided image using
    LSB steganography techniques. On top of this, a deterministic RNG algorithm
    is used to chaotically distrubute embed information.

    Params:
        filePath (str): The path to the image file selected for encoding.
        hash (str): The SHA-256 hash created by the fingerprint.
        key (str): A key provided by the user to embed and encrypt data.

    Returns:
        None
    """

    if key == DEFAULTPASS:
        print(
            "⚠ WARNING: Default fingerprint in use. This fingerprint is not secure ⚠\n"
        )

    encodingHeader = encodingSelection()
    if encodingHeader == None:
        encodingInformation(filePath, hash, key)

    encodedData = dataEncoder(encodingHeader, hash, key)
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

    mapping = generateSecureSample(key, encodeLimit, totalBits)

    for i in range(totalBits):
        currentPixel = math.ceil(mapping[i] / 3)
        xCoords = currentPixel % width
        yCoords = math.floor(currentPixel / width)
        currentChannel = mapping[i] % 3

        pixel = list(img[xCoords, yCoords])
        pixel[currentChannel] = (pixel[currentChannel] & ~1) | int(encodedData[i])
        img[xCoords, yCoords] = tuple(pixel)

    im.save(outputName)
    preserveMetadata(filePath, outputName)

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
    """
    Display the decoding menu and handle user input for decoding an image.

    Params:
        None

    Returns:
        None
    """

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
    """
    Decodes hidden information from a provided PNG image using a provided
    fingerprint.

    Params:
        filePath (str): The path to the image file selected for encoding.

    Returns:
        None
    """

    print(
        "★ Please enter your fingerprint. If left blank, the default fingerprint 'steganography' will be used. ★\n"
    )
    key = input("Please input your footprint: ")
    if key == "":
        key = DEFAULTPASS

    clearTerminal()
    print(f'★ Decoding data using fingerprint, "{key}" ★')

    hash = hashGenerator(key)
    firstHalf = slice(HASHHALF)
    lastHalf = slice(HASHHALF, HASHSIZE)
    firstFingerprint = hash[firstHalf]
    lastFingerprint = hash[lastHalf]

    im = Image.open(filePath)
    width, height = im.size
    totalBits = width * height * RGBCHANNELS

    lsbString = extractLSBBits(filePath, HASHHALF * BYTETOBIT, key)
    asciiOutput = bitsToAscii(lsbString)

    if firstFingerprint in asciiOutput:
        lsbString = extractLSBBits(filePath, totalBits - RGBCHANNELS, key)
        asciiOutput = bitsToAscii(lsbString)

        if lastFingerprint in asciiOutput:
            startIndex = asciiOutput.find(firstFingerprint)
            endIndex = asciiOutput.find(lastFingerprint)

            print(
                f"\n★ Verification Successful — the Fingerprint '{key}' is Correct. \n"
            )

            rawInformation = slice(startIndex + HASHHALF, endIndex)
            asciiOutput = decryptText(key, asciiOutput[rawInformation])

            if (EXTHEADER + TEXTHEADER) in asciiOutput:
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
