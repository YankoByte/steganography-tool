# COMP6841 - Steganography Project Helpers File

import os
import hashlib
from PIL import Image
import numpy as np
import math
from collections import Counter
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom
import base64

HASHSIZE = 64

RGBCHANNELS = 3
BYTETOKILOBYTE = 1 / 1000
BITTOBYTE = 1 / 8

VARWARNING = 500
ENTWARNING = 5

RCHAN = 0
GCHAN = 1
BCHAN = 2

TEMPKEY = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10'


def clearTerminal():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def stringToBinary(string):
    return "".join(format(ord(char), "08b") for char in string)


def hashGenerator(string):
    data = string.encode()
    return hashlib.sha256(data).hexdigest()


def dataEncoder(info, hash):
    firstHalf = slice(HASHSIZE // 2)
    lastHalf = slice(HASHSIZE // 2, HASHSIZE)

    firstFingerprint = hash[firstHalf]
    lastFingerprint = hash[lastHalf]
    encryptedData = encryptText(TEMPKEY, info)

    data = firstFingerprint + encryptedData + lastFingerprint
    return stringToBinary(data)

def encryptText(key, plainText):
    iv = urandom(16)
    
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    ciphertext = encryptor.update(plainText.encode()) + encryptor.finalize()
    
    return base64.b64encode(iv + ciphertext).decode('utf-8')

def decryptText(key, encryptedData) -> str:
    encrypted_data_bytes = base64.b64decode(encryptedData)
    
    iv = encrypted_data_bytes[:16]
    ciphertext = encrypted_data_bytes[16:]
    
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    return decrypted_data.decode('utf-8')

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
                    return "".join(bits)
    return "".join(bits)


def bitsToAscii(bitString):
    """Convert a binary string to its ASCII representation (truncates to full bytes)."""
    chars = []
    for i in range(0, len(bitString) - 7, 8):
        byte = bitString[i : i + 8]
        ascii_char = chr(int(byte, 2))
        chars.append(ascii_char)
    return "".join(chars)


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
    print("╔═══════════════ FILE STATS ═══════════════╗")
    print(f"║ Full File Directory: {filePath}    ║")
    print(f"║ File Name: {fileName}                   ║")
    print(f"║ File Size: {fileSize} kB                    ║")
    print(f"║ File Extension: {extension}               ║")
    print("╚══════════════════════════════════════════╝")


def printImageStats(filePath):
    im = Image.open(filePath)
    width, height = im.size
    encodeLimit = width * height * RGBCHANNELS * BITTOBYTE * BYTETOKILOBYTE

    print("╔═══════════════ IMAGE STATS ═════════════════╗")
    print(f"║ Dimensions: {width}px x {height}px         ║")
    print(f"║ Encodable Information: {encodeLimit} kB    ║")
    print("╚═════════════════════════════════════════════╝")


def printStegHeuristics(filePath):
    totalVariance = calcTotalVariance(filePath)
    totalEntropy = calcTotalEntropy(filePath)

    rVar = calcChannelVariance(filePath, RCHAN)
    gVar = calcChannelVariance(filePath, GCHAN)
    bVar = calcChannelVariance(filePath, BCHAN)

    rEnt = calcChannelEntropy(filePath, RCHAN)
    gEnt = calcChannelEntropy(filePath, GCHAN)
    bEnt = calcChannelEntropy(filePath, BCHAN)

    print("╔═════════════ STENOGRAPHIC HEURISTICS ═══════════════════════╗")
    print(f"║ Total Variance: {totalVariance}                                     ║")
    print(f"║ Channel Variance (RGB): [{rVar}, {gVar}, {bVar}]          ║")
    print(f"║ Entropy: {totalEntropy}                                               ║")
    print(f"║ Channel Entropy (RGB): [{rEnt}, {gEnt}, {bEnt}]                   ║")
    print("╚═════════════════════════════════════════════════════════════╝")

    if rEnt < ENTWARNING or gEnt < ENTWARNING or bEnt < ENTWARNING:
        print(
            "\n⚠ WARNING: One or more channels have low entropy. Consider a more complex image ⚠"
        )

    if rVar < VARWARNING or gVar < VARWARNING or bVar < VARWARNING:
        print(
            "\n⚠ WARNING: One or more channels have low variance. Consider a more complex image ⚠"
        )


def printEncodingSettings(numBits, numPixels, hash):
    print("\n╔═══════════════ ENCODING SETTINGS ═════════════════╗")
    print(f"║ Bits Encoded: {numBits} bits    ║")
    print(f"║ Pixels Used: {numPixels}    ║")
    print(f"║ Fingerprint Used: {hash}    ║")
    print("╚═════════════════════════════════════════════╝")

def printEncodingSelections():
    print("╔════════════════════ DATA INPUT MODE (WiP) ══════════════════════╗")
    print("║ Options                                                         ║")
    print("║ ★ Type '1' to manually enter plain text to encode.              ║")
    print("║ ★ Type '2' to load raw binary data from a file (any format).    ║")
    print("║                                                                 ║")
    print("╚═════════════════════════════════════════════════════════════════╝")
