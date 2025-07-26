# COMP6841 - Steganography Project Helpers File

import os
import hashlib
import numpy as np
import math
import base64
import re
from pathlib import Path
from PIL import Image
from collections import Counter
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom

HASHSIZE = 64

RGBCHANNELS = 3
BYTETOKILOBYTE = 1 / 1000
KILOBYTETOBYTE = 1000
BITTOBYTE = 1 / 8

VARWARNING = 500
ENTWARNING = 5

RCHAN = 0
GCHAN = 1
BCHAN = 2

EXTHEADER = "|EXT="
DEFAULTHEADER = "Text "

TEXTINPUT = "1"
FILEINPUT = "2"

DEFAULTHASH = "bfabba369a999a083b44f26c2da7bc52846cf39a872816d06969d2837840de6b"
DEFAULTSALT = b"TH1SH4SH1SN0T$IMPLE!!"

NOFILE = 1
INVALIDOPTION = 2
NOINFORMATION = 3
INVALIDMSG = 4


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


def dataEncoder(info, hash, fingerprint):
    firstHalf = slice(HASHSIZE // 2)
    lastHalf = slice(HASHSIZE // 2, HASHSIZE)

    firstFingerprint = hash[firstHalf]
    lastFingerprint = hash[lastHalf]
    key = passwordToKey(fingerprint, DEFAULTSALT)
    encryptedData = encryptText(key, info)

    data = firstFingerprint + encryptedData + lastFingerprint
    return stringToBinary(data)

def encryptText(key, plainText):
    iv = urandom(16)
    
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    ciphertext = encryptor.update(plainText.encode()) + encryptor.finalize()
    
    return base64.b64encode(iv + ciphertext).decode('utf-8')

def decryptText(key, encryptedData):
    encrypted_data_bytes = base64.b64decode(encryptedData)
    
    iv = encrypted_data_bytes[:16]
    ciphertext = encrypted_data_bytes[16:]
    
    key = passwordToKey(key, DEFAULTSALT)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    return decrypted_data.decode('utf-8')

def passwordToKey(password, salt):
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=16)
    return key

def writeToFile(decodedInformation, outputFilePath):
    binaryData = base64.b64decode(decodedInformation)
    with open(outputFilePath, 'wb') as f:
        f.write(binaryData)

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
    print("═══ FILE STATS ═══")
    print(f"Full File Directory: {filePath}")
    print(f"File Name: {fileName}")
    fileSizeConversion(fileSize)
    print(f"File Extension: {extension}\n")


def printImageStats(filePath):
    im = Image.open(filePath)
    width, height = im.size
    encodeLimit = width * height * RGBCHANNELS * BITTOBYTE * BYTETOKILOBYTE
    encodeLimit = round(encodeLimit, 2)

    print("═══ IMAGE STATS ═══")
    print(f"Dimensions: {width}px x {height}px")
    print(f"Encodable Information: {encodeLimit} kB\n")



def printStegHeuristics(filePath):
    totalVariance = calcTotalVariance(filePath)
    totalEntropy = calcTotalEntropy(filePath)

    rVar = calcChannelVariance(filePath, RCHAN)
    gVar = calcChannelVariance(filePath, GCHAN)
    bVar = calcChannelVariance(filePath, BCHAN)

    rEnt = calcChannelEntropy(filePath, RCHAN)
    gEnt = calcChannelEntropy(filePath, GCHAN)
    bEnt = calcChannelEntropy(filePath, BCHAN)

    print("═══ STENOGRAPHIC HEURISTICS ═══")
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

def encodingSelection():
    encodingHeader = EXTHEADER

    printEncodingSelections()
    encodingSelection = input("Option Selected: ").lower()

    if encodingSelection == TEXTINPUT:
        encodingHeader += DEFAULTHEADER

        info = input("Enter text to encode: ")
        if info == "":
            clearTerminal()
            printError(INVALIDMSG)
            encodingSelection
        encodingHeader += info

    elif encodingSelection == FILEINPUT:
        print("\n★ Enter the full file path (including name and extension) ★")
        filePath = input("Full File Directory: ")
        if os.path.isfile(filePath) == False:
            clearTerminal()
            printError(NOFILE)
            encodingSelection()

        fileName = os.path.basename(filePath)
        encodingHeader += "$"
        encodingHeader += fileName
        encodingHeader += "$"

        print(f"DEBUG REMOVE LATER ENCODING HEADER {encodingHeader}")

        with open(filePath, "rb") as imageFile:
            info = base64.b64encode(imageFile.read()).decode('utf-8')
            encodingHeader += info
    else:
        clearTerminal()
        printError(INVALIDOPTION)
        encodingSelection()

    return encodingHeader

def encodingErrorDisplay(totalBits, encodeLimit):
    print("\n⚠ WARNING: The data you're trying to encode exceeds the image's capacity")
    print(f"  ★ Required bits: {totalBits}")
    print(f"  ★ Max capacity: {encodeLimit}\n")
    input("Press Enter to Continue...")

    clearTerminal()
    print("★ Returning to encoding information... ★\n")

def extractName(text):
    name = re.search(r'\$(.*?)\$', text)
    if name:
        return name.group(1)
    return None

def displayExitMenu():
    print("\nThank you for using Stego Tools, goodbye!")
    input("Press Enter to Continue...")
    exit()

def printDecodedInformation(inputType, asciiOutput):
    print("═══ INFORMATION METADATA ═══")
    if inputType == TEXTINPUT:
        decodedInformation = asciiOutput[len(EXTHEADER + DEFAULTHEADER):]
        print(f"Information Format: Plaintext")
        print(f"Decoded Information: {decodedInformation}")
    else:
        decodedInformation = asciiOutput[len(EXTHEADER):]
        extractedFile = extractName(decodedInformation)
        nameLength = len(extractedFile) + 2
        decodedInformation = asciiOutput[len(EXTHEADER) + nameLength:]

        file = Path(extractedFile)
        extension = file.suffix.lstrip('.')
        scriptDir = os.path.dirname(os.path.abspath(__file__))
        outputName = scriptDir
        outputName += "\\"
        outputName += extractedFile
        
        print(f"Information Format: {extension}")
        print(f"Original Filename: {extractedFile}")
        print(f"Decoded Information: {decodedInformation}")
        print(f"Default Output Name: {outputName}")

        print("\n★ Please Enter a Name for the Output File (default: output.png) ★")
        outputPath = input("Output Name: ")
        if outputPath == "":
            outputPath = outputName

        writeToFile(decodedInformation.encode(), outputPath)

def printError(errorType):
    if errorType == NOFILE:
        print("❗ Error - File Does Not Exist! ❗\n")
    elif errorType == INVALIDOPTION:
        print("❗ Error - Please Type a Valid Option ❗\n")
    elif errorType == NOINFORMATION:
        print("\n❗ Error - no Information Could be Found ❗")
    elif errorType == INVALIDMSG:
        print("❗ Error - Please Provide a Valid Message to Encode. ❗\n")

def fileSizeConversion(fileSize):
    fileSize = fileSize * KILOBYTETOBYTE
    power = math.log(fileSize, KILOBYTETOBYTE)

    if power < 1:
        print(f"File Size: {fileSize} B")
    elif power < 2:
        fileSize = fileSize * BYTETOKILOBYTE
        fileSize = round(fileSize, 2)
        print(f"File Size: {fileSize} kB")
    elif power < 3:
        fileSize = fileSize * BYTETOKILOBYTE * BYTETOKILOBYTE
        fileSize = round(fileSize, 2)
        print(f"File Size: {fileSize} mB")
    else:
        fileSize = fileSize * BYTETOKILOBYTE * BYTETOKILOBYTE * BYTETOKILOBYTE
        fileSize = round(fileSize, 2)
        print(f"File Size: {fileSize} gB")