# COMP6841 - Steganography Project Helpers File

import os
import hashlib
from PIL import Image
import numpy as np
import math
from collections import Counter

HASHSIZE = 64

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

def extractLSBBits(fileDirectory, totalBits):
    """Return a string of the first n_bits LSBs from the image’s RGB channels."""
    im = Image.open(fileDirectory).convert("RGB")
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

def calcTotalVariance(fileDirectory):
    img = Image.open(fileDirectory).convert('RGB')
    pixels = np.array(img)
    return round(np.var(pixels), 2)

def calcRedVariance(fileDirectory):
    img = Image.open(fileDirectory).convert('RGB')
    data = np.array(img)

    redChannel = data[:, :, 0].flatten()
    return round(np.var(redChannel), 2)

def calcGreenVariance(fileDirectory):
    img = Image.open(fileDirectory).convert('RGB')
    data = np.array(img)

    greenChannel = data[:, :, 1].flatten()
    return round(np.var(greenChannel), 2)

def calcBlueVariance(fileDirectory):
    img = Image.open(fileDirectory).convert('RGB')
    data = np.array(img)

    blueChannel = data[:, :, 2].flatten()
    return round(np.var(blueChannel), 2)

def calcTotalEntropy(fileDirectory):
    img = Image.open(fileDirectory).convert('L')
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

def calcRedEntropy(fileDirectory):
    img = Image.open(fileDirectory).convert('RGB')
    data = np.array(img)

    redChannel = data[:, :, 0].flatten()
    return round(calcChannelEntropy(redChannel), 2)

def calcGreenEntropy(fileDirectory):
    img = Image.open(fileDirectory).convert('RGB')
    data = np.array(img)

    greenChannel = data[:, :, 1].flatten()
    return round(calcChannelEntropy(greenChannel), 2)

def calcBlueEntropy(fileDirectory):
    img = Image.open(fileDirectory).convert('RGB')
    data = np.array(img)

    blueChannel = data[:, :, 2].flatten()
    return round(calcChannelEntropy(blueChannel), 2)