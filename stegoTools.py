# COMP6841 - Steganography Project

from PIL import Image
from Helpers import *
import os
import math

ENCODE = "1"
DECODE = "2"
RETURNMAIN = "return"
QUITAPP = "quit"
QUITNUMBER = "3"
EXTPNG = ".png"

BYTETOKILOBYTE = 1 / 1000
BITTOBYTE = 1 / 8
RGBCHANNELS = 3
BYTETOBIT = 8

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

# Note to self, the plaintext is "steganography"
DEFAULTHASH = "bfabba369a999a083b44f26c2da7bc52846cf39a872816d06969d2837840de6b"

print("★ Stego Tools v1.4 ★\n")


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
        print("\nThank you for using Stego Tools v1.4. Goodbye!")
        input("Press Enter to Continue...")
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
        print("❗ Error - File Does Not Exist! ❗\n")
        encodeMenu()


def encodingSettings(filePath):
    size = os.path.getsize(filePath) * BYTETOKILOBYTE
    fileName = os.path.basename(filePath)
    extension = os.path.splitext(filePath)[1]

    printFileStats(filePath, fileName, size, extension)

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
        print("❗ Error - Please Type a Valid Option ❗\n")
        encodingSettings(filePath)


def encodingFingerprint(filePath):
    hash = DEFAULTHASH
    fileName = os.path.basename(filePath)

    print(f'★ Do you want to use a custom fingerprint to identify "{fileName}"? ★')
    fingerprintChoice = input('Enter "yes" or "no": ').lower()
    if fingerprintChoice == CONFIRM or fingerprintChoice == CONFIRM2:
        fingerprint = input("Enter Fingerprint: ")

        if fingerprint == "":
            hash = "bfabba369a999a083b44f26c2da7bc52846cf39a872816d06969d2837840de6b"
        else:
            hash = hashGenerator(fingerprint)
    elif fingerprintChoice != DENY and fingerprintChoice != DENY2:
        clearTerminal()
        print("❗ Error - Please Type a Valid Option ❗\n")
        encodingFingerprint(filePath)

    print(f"\n★ Fingerprint has been created: {hash} ★\n")

    input("Press Enter to Continue...")
    clearTerminal()

    print("★ Success — Proceeding to Encoding Settings... ★\n")
    encodingInformation(filePath, hash)


def encodingInformation(filePath, hash):
    if hash == DEFAULTHASH:
        print(
            "⚠ WARNING: Default fingerprint in use. This fingerprint is not secure ⚠\n"
        )

    info = input("Enter information to encode: ")

    if info == "":
        clearTerminal()
        print("⚠ Error - Please Provide a Valid Message to Encode. ⚠\n")
        encodingInformation(filePath, hash)

    encodedData = dataEncoder(info, hash)
    totalBits = len(encodedData)
    totalPixels = math.ceil(totalBits / 3)

    encodingSettings(totalBits, totalPixels, hash)

    print("\n★ Would you like to proceed with encoding this message? ★")
    confirmation = input('Enter "yes" or "no": ').lower()
    if confirmation == DENY or confirmation == DENY2:
        clearTerminal()
        print("★ Returning to encoding menu... ★\n")
        encodeMenu()
    elif confirmation != CONFIRM and confirmation != CONFIRM2:
        clearTerminal()
        print("❗ Error - Please Type a Valid Option ❗\n")
        encodingInformation(filePath, hash)

    print("\n★ Please Enter a Name for the Output File (default: output.png) ★")
    outputName = input("Output Name: ")
    if outputName == "":
        outputName = "output.png"
    else:
        outputName += ".png"

    im = Image.open(filePath)
    img = im.load()
    width, height = im.size

    for i in range(totalPixels):
        currentX = i % width
        currentY = math.floor(i / width)

        pixel = list(img[currentX, currentY])

        for j in range(RGBCHANNELS):
            bitIndex = i * 3 + j
            if bitIndex >= totalBits:
                break

            pixel[j] = (pixel[j] & ~1) | int(encodedData[bitIndex])

        img[currentX, currentY] = tuple(pixel)
        pixel = list(img[currentX, currentY])

    im.save(outputName)
    print(
        f'\n★ Success — Information has been Successfully Embedded Into "{outputName}". ★'
    )

    print('\n★ Press Enter to return to the menu, or type "quit" to exit. ★')
    menuSelection = input("Option Selected: ").lower()
    if menuSelection == QUITAPP:
        print("\nThank you for using Stego Tools v1.4. Goodbye!")
        input("Press Enter to Continue...")
        quit()

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
        print("❗ Error - File Does Not Exist! ❗\n")
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

    lsbString = extractLSBBits(filePath, totalBits)
    # print(f"\nFirst {len(lsb_string)} LSB bits:\n{lsb_string}")

    asciiOutput = bitsToAscii(lsbString)
    # print(f"\nASCII Output:\n{asciiOutput}")

    if firstFingerprint in asciiOutput and lastFingerprint in asciiOutput:
        startIndex = asciiOutput.find(firstFingerprint)
        endIndex = asciiOutput.find(lastFingerprint)

        print(
            f"\n★ Verification Successful — the Fingerprint '{hashPlainText}' is Correct. \n"
        )

        print("╔═══ ENCODED INFORMATION ════╗")
        print(f"║ Message Start Index: {startIndex + HASHHALF}    ║")
        print(f"║ Message End Index: {endIndex - 1}      ║    ")
        print(
            f"║ Message Length: {endIndex - startIndex - HASHHALF}          ║    "
        )
        print("╚════════════════════════════╝")

        actualInformation = slice(startIndex + HASHHALF, endIndex)
        print(f"Decoded Information: {asciiOutput[actualInformation]}")
    else:
        print("\n❗ Error - no Information Could be Found ❗")

    print('\n★ Press Enter to return to the menu, or type "quit" to exit. ★')
    menuSelection = input("Option Selected: ").lower()
    if menuSelection == QUITAPP:
        print("\nThank you for using Stego Tools v1.4. Goodbye!")
        input("Press Enter to Continue...")
        quit()

    clearTerminal()
    print("★ Returning to Main Menu... ★\n")
    mainMenu()


mainMenu()
