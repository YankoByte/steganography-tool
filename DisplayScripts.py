import os
import numpy as np
import math
from PIL import Image
from collections import Counter

RGBCHANNELS = 3
BYTETOKILOBYTE = 1 / 1000
KILOBYTETOBYTE = 1000
BITTOBYTE = 1 / 8

VARWARNING = 500
ENTWARNING = 5

RCHAN = 0
GCHAN = 1
BCHAN = 2

NOFILE = 0
INVALIDOPTION = 1
NOINFORMATION = 2
INVALIDMSG = 3

FILESIZE = 0
ENCODABLEINFO = 1

def fileSizeConversion(fileSize, displayInfo):
    startingText = None

    if displayInfo == FILESIZE:
        startingText = "File Size:"
    else:
        startingText = "Encodable Information:"


    fileSize = fileSize * KILOBYTETOBYTE
    power = math.log(fileSize, KILOBYTETOBYTE)

    if power < 1:
        print(f"{startingText} {fileSize} B")
    elif power < 2:
        fileSize = fileSize * BYTETOKILOBYTE
        fileSize = round(fileSize, 2)
        print(f"{startingText} {fileSize} kB")
    elif power < 3:
        fileSize = fileSize * BYTETOKILOBYTE * BYTETOKILOBYTE
        fileSize = round(fileSize, 2)
        print(f"{startingText} {fileSize} mB")
    else:
        fileSize = fileSize * BYTETOKILOBYTE * BYTETOKILOBYTE * BYTETOKILOBYTE
        fileSize = round(fileSize, 2)
        print(f"{startingText} {fileSize} gB")

def printError(errorType):
    if errorType == NOFILE:
        print("❗ Error - File Does Not Exist! ❗\n")
    elif errorType == INVALIDOPTION:
        print("❗ Error - Please Type a Valid Option ❗\n")
    elif errorType == NOINFORMATION:
        print("\n❗ Error - no Information Could be Found ❗")
    elif errorType == INVALIDMSG:
        print("❗ Error - Please Provide a Valid Message to Encode. ❗\n")

def displayExitMenu():
    print("\nThank you for using Stego Tools, goodbye!")
    input("Press Enter to Continue...")
    exit()

def encodingErrorDisplay(totalBits, encodeLimit):
    print("\n⚠ WARNING: The data you're trying to encode exceeds the image's capacity")
    print(f"  ★ Required bits: {totalBits}")
    print(f"  ★ Max capacity: {encodeLimit}\n")
    input("Press Enter to Continue...")

    clearTerminal()
    print("★ Returning to encoding information... ★\n")

def printEncodingSettings(numBits, numPixels, hash):
    print("\n═══ ENCODING SETTINGS ═══")
    print(f"Bits Encoded: {numBits} bits")
    print(f"Pixels Used: {numPixels}")
    print(f"Fingerprint Used: {hash}")

def printEncodingSelections():
    print("╔════════════════════ DATA INPUT MODE (WiP) ══════════════════════╗")
    print("║ Options                                                         ║")
    print("║ ★ Type '1' to manually enter plain text to encode.              ║")
    print("║ ★ Type '2' to load raw binary data from a file (any format).    ║")
    print("║                                                                 ║")
    print("╚═════════════════════════════════════════════════════════════════╝")

def printStegHeuristics(filePath):
    totalVariance = calcTotalVariance(filePath)
    totalEntropy = calcTotalEntropy(filePath)

    rVar = calcChannelVariance(filePath, RCHAN)
    gVar = calcChannelVariance(filePath, GCHAN)
    bVar = calcChannelVariance(filePath, BCHAN)

    rEnt = calcChannelEntropy(filePath, RCHAN)
    gEnt = calcChannelEntropy(filePath, GCHAN)
    bEnt = calcChannelEntropy(filePath, BCHAN)

    print("\n═══ STENOGRAPHIC HEURISTICS ═══")
    print(f"Total Variance: {totalVariance}")
    print(f"Channel Variance: [{rVar}, {gVar}, {bVar}] (R,G,B)")
    print(f"Entropy: {totalEntropy}")
    print(f"Channel Entropy: [{rEnt}, {gEnt}, {bEnt}] (R,G,B)")

    if rEnt < ENTWARNING or gEnt < ENTWARNING or bEnt < ENTWARNING:
        print(
            "\n⚠ WARNING: One or more channels have low entropy. Consider a more complex image ⚠"
        )

    if rVar < VARWARNING or gVar < VARWARNING or bVar < VARWARNING:
        print(
            "\n⚠ WARNING: One or more channels have low variance. Consider a more complex image ⚠"
        )

def printEncodingMenu():
    print("╔═════════════════════ ENCODING MENU (WiP) ═════════════════════╗")
    print("║ Options                                                       ║")
    print("║ ★ Enter the full file path (including name and extension)     ║")
    print("║    to select an image for encoding.                           ║")
    print("║                                                               ║")
    print('║ ★ To return to the main menu, type "return".                  ║')
    print("╚═══════════════════════════════════════════════════════════════╝")


def printMainMenu():
    print("╔══════ MAIN MENU ═════╗")
    print("║ Options              ║")
    print("║ 1. Encoding Suite    ║")
    print("║ 2. Decoding Suite    ║")
    print("║ 3. Quit App          ║")
    print("╚══════════════════════╝")


def printDecodeMenu():
    print("╔═════════════════════ DECODING MENU (WiP) ═════════════════════╗")
    print("║ Options                                                       ║")
    print("║ ★ Enter the full file path (including name and extension)     ║")
    print("║    to select an image for decoding.                           ║")
    print("║                                                               ║")
    print('║ ★ To return to the main menu, type "return".                  ║')
    print("╚═══════════════════════════════════════════════════════════════╝")


def printFileStats(filePath, fileName, fileSize, extension):
    print("═══ FILE STATS ═══")
    print(f"Full File Directory: {filePath}")
    print(f"File Name: {fileName}")
    fileSizeConversion(fileSize, FILESIZE)
    print(f"File Extension: {extension}\n")


def printImageStats(filePath):
    im = Image.open(filePath)
    width, height = im.size
    encodeLimit = width * height * RGBCHANNELS * BITTOBYTE * BYTETOKILOBYTE

    print("═══ IMAGE STATS ═══")
    print(f"Dimensions: {width}px x {height}px")
    fileSizeConversion(encodeLimit, ENCODABLEINFO)

def calcTotalVariance(filePath):
    img = Image.open(filePath).convert("RGB")
    pixels = np.array(img)
    return round(np.var(pixels), 2)

def calcChannelVariance(filePath, channel):
    img = Image.open(filePath).convert("RGB")
    data = np.array(img)

    channelData = data[:, :, channel].flatten()
    return round(np.var(channelData), 2)


def calcTotalEntropy(filePath):
    img = Image.open(filePath).convert("L")
    return round(img.entropy(), 2)


def calcChannelEntropy(filePath, channel):
    img = Image.open(filePath).convert("RGB")
    data = np.array(img)
    channelData = data[:, :, channel].flatten()

    counts = Counter(channelData)
    total = len(channelData)
    entropy = 0.0

    for count in counts.values():
        p = count / total
        entropySum = p * math.log2(p)
        entropy -= entropySum

    return round(entropy, 2)

def clearTerminal():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")