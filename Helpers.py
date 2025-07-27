# COMP6841 - Steganography Project Helpers File

import base64
import hashlib
import math
import os
import re
from os import urandom
from pathlib import Path

from blake3 import blake3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from PIL import Image

from DisplayScripts import *

HASHSIZE = 64

RGBCHANNELS = 3

EXTHEADER = "|EXT="
DEFAULTHEADER = "Text "

TEXTINPUT = "1"
FILEINPUT = "2"

DEFAULTSALT = b"TH1SH4SH1SN0T$IMPLE!!"

NOFILE = 0
INVALIDOPTION = 1
NOINFORMATION = 2
INVALIDMSG = 3


def hashGenerator(string):
    # Given a string, returns a SHA256 from the input

    data = string.encode()
    return hashlib.sha256(data).hexdigest()


def passwordToKey(password, salt):
    # Given a cleartext password, creates a 16 byte key

    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000, dklen=16)
    return key


def encryptText(key, plainText):
    # Given a plaintext and a key, encrypts text using AES encryption

    iv = urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    ciphertext = encryptor.update(plainText.encode()) + encryptor.finalize()

    return base64.b64encode(iv + ciphertext).decode("utf-8")


def decryptText(key, encryptedData):
    # Given a ciphertext and a key, decrypts text using AES encryption

    encrypted_data_bytes = base64.b64decode(encryptedData)

    iv = encrypted_data_bytes[:16]
    ciphertext = encrypted_data_bytes[16:]

    key = passwordToKey(key, DEFAULTSALT)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    return decrypted_data.decode("utf-8")


def generateSecureSample(key, limit, count):
    # Given a key, creates a random uniformly distrubuted permutation of
    # 'count' numbers with a maximum number of 'limit'

    limit = limit - RGBCHANNELS
    indices = list(range(limit))

    hasher = blake3(key.encode())
    random_bytes = hasher.digest(length=8 * limit)

    # Fisher-Yates shuffle to generate deterministically random permutation
    for i in reversed(range(1, limit)):
        start = (i * 8) % len(random_bytes)
        val = int.from_bytes(random_bytes[start : start + 8], "big")

        j = val % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]

    return indices[:count]


def stringToBinary(string):
    # Given a string, converts it to binary

    return "".join(format(ord(char), "08b") for char in string)


def dataEncoder(info, hash, fingerprint):
    # Given info encoded as a base64 string, a hash and a fingerprint
    # combines the data into a structured message and then encrypting it

    firstHalf = slice(HASHSIZE // 2)
    lastHalf = slice(HASHSIZE // 2, HASHSIZE)

    firstFingerprint = hash[firstHalf]
    lastFingerprint = hash[lastHalf]
    key = passwordToKey(fingerprint, DEFAULTSALT)
    encryptedData = encryptText(key, info)

    data = firstFingerprint + encryptedData + lastFingerprint
    return stringToBinary(data)


def extractLSBBits(filePath, totalBits, key):
    # Given a filePath, totalBits and a key, attempts to decode embedded
    # information via LSB bit mask and extracting

    im = Image.open(filePath).convert("RGB")
    pixels = im.load()
    width, height = im.size
    encodeLimit = width * height * RGBCHANNELS

    # Deterministically random permutation to embed bits in
    mapping = generateSecureSample(key, encodeLimit, totalBits)

    bits = []
    for i in range(totalBits):
        currentPixel = math.ceil(mapping[i] / 3)
        currentChannel = mapping[i] % 3

        x = currentPixel % width
        y = math.floor(currentPixel / width)

        pixel = pixels[x, y]
        bits.append(str(pixel[currentChannel] & 1))

    return "".join(bits)


def bitsToAscii(bitString):
    # Given the binary data bitString, converts bits into ascii characters

    chars = []
    for i in range(0, len(bitString) - 7, 8):
        byte = bitString[i : i + 8]
        ascii_char = chr(int(byte, 2))
        chars.append(ascii_char)
    return "".join(chars)


def writeToFile(decodedInformation, outputFilePath):
    # Given decodedInformation and an outputFilePath, saves decoded information
    # into a provided file.

    binaryData = base64.b64decode(decodedInformation)
    with open(outputFilePath, "wb") as f:
        f.write(binaryData)


def encodingSelection():
    # Helper function for encodingInformation() to help handle encoding file
    # and text inputs

    encodingHeader = EXTHEADER

    printEncodingSelections()
    encodingSelection = input("Option Selected: ").lower()

    if encodingSelection == TEXTINPUT:
        encodingHeader += DEFAULTHEADER

        info = input("Enter text to encode: ")
        if info == "":
            clearTerminal()
            printError(INVALIDMSG)
            return None

        encodingHeader += info

    elif encodingSelection == FILEINPUT:
        print("\n★ Enter the full file path (including name and extension) ★")
        filePath = input("Full File Directory: ")
        if os.path.isfile(filePath) == False:
            clearTerminal()
            printError(NOFILE)
            return None

        fileName = os.path.basename(filePath)
        encodingHeader += "$"
        encodingHeader += fileName
        encodingHeader += "$"

        with open(filePath, "rb") as imageFile:
            info = base64.b64encode(imageFile.read()).decode("utf-8")
            encodingHeader += info
    else:
        clearTerminal()
        printError(INVALIDOPTION)
        return None

    return encodingHeader


def printDecodedInformation(inputType, asciiOutput):
    # Given an inputType and asciiOutput, attempts to decode the embedded 
    # information along with the metadata stored

    print("═══ INFORMATION METADATA ═══")
    if inputType == TEXTINPUT:
        decodedInformation = asciiOutput[len(EXTHEADER + DEFAULTHEADER) :]
        print(f"Information Format: Plaintext")
        print(f"Decoded Information: {decodedInformation}")
    else:
        decodedInformation = asciiOutput[len(EXTHEADER) :]
        extractedFile = extractName(decodedInformation)
        nameLength = len(extractedFile) + 2
        decodedInformation = asciiOutput[len(EXTHEADER) + nameLength :]

        file = Path(extractedFile)
        extension = file.suffix.lstrip(".")
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


def extractName(text):
    # Given text, finds the first substring between two dollar signs ($), and
    # returns it, in this case the name metadata is stored

    name = re.search(r"\$(.*?)\$", text)
    if name:
        return name.group(1)
    return None
