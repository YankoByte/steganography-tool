# COMP6841 - Steganography Project Helpers File

import os
import hashlib
from PIL import Image
import numpy as np
import math
from collections import Counter

HASHSIZE = 64

RGBCHANNELS = 3
BYTETOKILOBYTE = 1/1000
BITTOBYTE = 1/8

VARWARNING = 500
ENTWARNING = 5

def clearTerminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def stringToBinary(string):
    return ''.join(format(ord(char), '08b') for char in string)

def hashGenerator(string):
    data = string.encode()
    return hashlib.sha256(data).hexdigest()

def dataEncoder(info, hash):
    firstHalf = slice(HASHSIZE//2)
    lastHalf = slice(HASHSIZE//2, HASHSIZE)

    firstFingerprint = hash[firstHalf]
    lastFingerprint = hash[lastHalf]

    data = firstFingerprint + info + lastFingerprint
    return stringToBinary(data)

def extractLSBBits(filePath, totalBits):
    """Return a string of the first n_bits LSBs from the image’s RGB channels."""
    im = Image.open(filePath).convert("RGB")
    pixels = im.load()
    width, height = im.size

    bits = []
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            for channel in (r, g, b):
                bits.append(str(channel & 1))
                if len(bits) == totalBits:
                    return ''.join(bits)
    return ''.join(bits)

def bitsToAscii(bitString):
    """Convert a binary string to its ASCII representation (truncates to full bytes)."""
    chars = []
    for i in range(0, len(bitString) - 7, 8):
        byte = bitString[i:i+8]
        ascii_char = chr(int(byte, 2))
        chars.append(ascii_char)
    return ''.join(chars)

def calcTotalVariance(filePath):
    img = Image.open(filePath).convert('RGB')
    pixels = np.array(img)
    return round(np.var(pixels), 2)

def calcRedVariance(filePath):
    img = Image.open(filePath).convert('RGB')
    data = np.array(img)

    redChannel = data[:, :, 0].flatten()
    return round(np.var(redChannel), 2)

def calcGreenVariance(filePath):
    img = Image.open(filePath).convert('RGB')
    data = np.array(img)

    greenChannel = data[:, :, 1].flatten()
    return round(np.var(greenChannel), 2)

def calcBlueVariance(filePath):
    img = Image.open(filePath).convert('RGB')
    data = np.array(img)

    blueChannel = data[:, :, 2].flatten()
    return round(np.var(blueChannel), 2)

def calcTotalEntropy(filePath):
    img = Image.open(filePath).convert('L')
    return round(img.entropy(), 2)

def calcChannelEntropy(channelData):
    counts = Counter(channelData)
    total = len(channelData)
    entropy = 0.0

    for count in counts.values():
        p = count/total
        entropySum = p * math.log2(p)
        entropy -= entropySum

    return entropy

def calcRedEntropy(filePath):
    img = Image.open(filePath).convert('RGB')
    data = np.array(img)

    redChannel = data[:, :, 0].flatten()
    return round(calcChannelEntropy(redChannel), 2)

def calcGreenEntropy(filePath):
    img = Image.open(filePath).convert('RGB')
    data = np.array(img)

    greenChannel = data[:, :, 1].flatten()
    return round(calcChannelEntropy(greenChannel), 2)

def calcBlueEntropy(filePath):
    img = Image.open(filePath).convert('RGB')
    data = np.array(img)

    blueChannel = data[:, :, 2].flatten()
    return round(calcChannelEntropy(blueChannel), 2)

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

def printFileStats(filePath, fileName, size, extension):
    print("╔═══════════════ FILE STATS ═══════════════╗")
    print(f'║ Full File Directory: {filePath}    ║')
    print(f"║ File Name: {fileName}                   ║")
    print(f'║ File Size: {size} kB                    ║')
    print(f'║ File Extension: {extension}               ║')
    print("╚══════════════════════════════════════════╝")

def printImageStats(filePath):
    im = Image.open(filePath)
    width, height = im.size
    encodeLimit = width * height * RGBCHANNELS * BITTOBYTE * BYTETOKILOBYTE

    print("╔═══════════════ IMAGE STATS ═════════════════╗")
    print(f'║ Dimensions: {width}px x {height}px         ║')
    print(f"║ Encodable Information: {encodeLimit} kB    ║")
    print("╚═════════════════════════════════════════════╝")


def printStegHeuristics(filePath):
    totalVariance = calcTotalVariance(filePath)
    totalEntropy = calcTotalEntropy(filePath)

    rVar = calcRedVariance(filePath)
    gVar = calcGreenVariance(filePath)
    bVar = calcBlueVariance(filePath)

    rEnt = calcRedEntropy(filePath)
    gEnt = calcGreenEntropy(filePath)
    bEnt = calcBlueEntropy(filePath)

    print("╔═════════════ STENOGRAPHIC HEURISTICS ═══════════════════════╗")
    print(f'║ Total Variance: {totalVariance}                                     ║')
    print(f'║ Channel Variance (RGB): [{rVar}, {gVar}, {bVar}]          ║')
    print(f'║ Entropy: {totalEntropy}                                               ║')
    print(f'║ Channel Entropy (RGB): [{rEnt}, {gEnt}, {bEnt}]                   ║')
    print("╚═════════════════════════════════════════════════════════════╝")

    if (rEnt < ENTWARNING or gEnt < ENTWARNING or bEnt < ENTWARNING):
        print("\n⚠ WARNING: One or more channels have low entropy. Consider a more complex image ⚠")

    if (rVar < VARWARNING or gVar < VARWARNING or bVar < VARWARNING):
        print("\n⚠ WARNING: One or more channels have low variance. Consider a more complex image ⚠")

def encodingSettings(numBits, numPixels, hash):
    print("\n╔═══════════════ ENCODING SETTINGS ═════════════════╗")
    print(f'║ Bits Encoded: {numBits} bits    ║')
    print(f"║ Pixels Used: {numPixels}    ║")
    print(f"║ Fingerprint Used: {hash}    ║")
    print("╚═════════════════════════════════════════════╝")