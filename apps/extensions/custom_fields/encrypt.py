from django.db import models
from django import forms
import base64
XOR_KEY = 0x88
encryption_header_notin_field = u'+'   #used to encrypt tag not when in modelsfield
encryption_header = u'^'
encryption_booter = u'$'

#used to encrypt decode not when in modelsfield
def decode_notin_field(value):
    if value.startswith(encryption_header_notin_field):
        value = base64.b64decode(value[len(encryption_header_notin_field):-len(encryption_booter)])
    return value

#used to encrypt decode when in modelsfield
def to_python_encrypt(value):
    if type(value) in (unicode,) and value.startswith(encryption_header) and value.endswith(encryption_booter):
        value = base64.b64decode(value[len(encryption_header):-len(encryption_booter)])
        value = value.decode('utf-8')
    return value

#used to encrypt encode when in and not in modelsfield
def get_prep_value_encrypt(value,encryption_header_tag):
    encryptstr = value
    if type(value) in (str,):
        if not value.startswith(encryption_header.encode('ascii','ignore')) and not value.startswith(encryption_header_notin_field.encode('ascii','ignore')):
            encryptstr = encryption_header_tag.encode('ascii','ignore')+base64.b64encode(value)+encryption_booter.encode('ascii','ignore')
            encryptstr = encryptstr.decode('unicode-escape')
    if type(value) in (unicode,):
        if not value.startswith(encryption_header) and not value.startswith(encryption_header_notin_field):
            value = value.encode('UTF-8')
            encryptstr = encryption_header_tag+base64.b64encode(value)+encryption_booter
    return encryptstr

#TODO:not used in form when has chinese
class Base64Field(models.Field):
    __metaclass__ = models.SubfieldBase 

    def __init__(self, *args, **kwargs):
        super(Base64Field, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'text'
    
    def to_python(self, value):
        return to_python_encrypt(value)

    def get_prep_value(self, value):
        return get_prep_value_encrypt(value,encryption_header)
    
class XORField(models.Field):
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        super(XORField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'text'
    
    def to_python(self, value):
        #todo improve later
        if type(value) in (unicode,) and value.startswith(encryption_header) and value.endswith(encryption_booter):
            value = (''.join([chr(ord(x) ^ XOR_KEY) for x in value[len(encryption_header):-len(encryption_booter)].decode('hex')]))
        return value

    def get_prep_value(self, value):
        if type(value) in (unicode,):
            value = value.encode('UTF-8')
        return encryption_header+(''.join([chr(ord(x) ^ XOR_KEY) for x in value])).encode('hex')+encryption_booter
    
    
    