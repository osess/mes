"""Generate test images for EAN13 barcode encoder"""

from __init__ import EAN13Encoder
from eantest import EAN13Test


for index, string in enumerate(EAN13Test.test_strings):
    enc = EAN13Encoder(string)
    enc.save("hubarcode/ean13/test_img/%d.png" % (index + 1))
