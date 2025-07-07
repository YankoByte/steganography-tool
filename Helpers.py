# COMP6841 - Steganography Project Helpers File

import os
import hashlib

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