#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from base64 import b64encode, encodebytes
from tokenize import Ignore
from Crypto.Cipher import AES
import binascii
import hashlib
from string import printable
import base64

BS = AES.block_size


def padding_pkcs5(value):
    return str.encode(value + (BS - len(value) % BS) * chr(BS - len(value) % BS))


def padding_zero(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)


def aes_ecb_encrypt(key, value):
    ''' AES/ECB/NoPadding encrypt '''
    key = bytes.fromhex(key)
    cryptor = AES.new(key, AES.MODE_ECB)
    ciphertext = cryptor.encrypt(bytes.fromhex(value))
    return ''.join(['%02x' % i for i in ciphertext]).upper()

def aes_ecb_encrypt_padding_pkcs5(key, value):
    # AES/ECB/PKCS5padding
    # key is sha1prng encrypted before
    cryptor = AES.new(bytes.fromhex(key), AES.MODE_ECB)
    padding_value = padding_pkcs5(value)  # padding content with pkcs5
    ciphertext = cryptor.encrypt(padding_value)
    # 填充
    return ''.join(['%02x' % i for i in ciphertext]).upper()


def aes_ecb_decrypt(key:str, value:str) -> str:
    ''' AES/ECB/NoPadding decrypt '''
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    key = bytes.fromhex(key)
    cryptor = AES.new(key, AES.MODE_ECB)
    base64_decrypted = base64.decodebytes(value.encode(encoding='utf-8').strip())
    # ciphertext = cryptor.decrypt(base64_decrypted)
    # new_string = ''.join(char for char in ciphertext.decode('ISO-8859-1') if char in printable)
    # return new_string
    decrypted_text = str(cryptor.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
    decrypted_text1 = unpad(decrypted_text)
    return decrypted_text1


def get_userkey(key, value):
    ''' AES/ECB/PKCS5Padding encrypt '''
    cryptor = AES.new(bytes.fromhex(key), AES.MODE_ECB)
    padding_value = padding_pkcs5(value)
    ciphertext = cryptor.encrypt(padding_value)
    # 填充
    return ''.join(['%02x' % i for i in ciphertext]).upper()


def get_sha1prng_key(key):
    '''[summary]
    encrypt key with SHA1PRNG
    same as java AES crypto key generator SHA1PRNG
    Arguments:
        key {[string]} -- [key]

    Returns:
        [string] -- [hexstring]
    '''
    signature = hashlib.sha1(key.encode()).digest()
    signature = hashlib.sha1(signature).digest()
    return ''.join(['%02x' % i for i in signature]).upper()[:32]


# test 
#hexstr_content = 'root@1234'  # content
#key = '5fT0np!je&4@sztest.comaddition'  # keypassword

# 解密
#aes128string = aes_ecb_decrypt(get_sha1prng_key(key), 'HLfdRPCd5dtDtZlULTpNuQ==')
#print(aes128string)
