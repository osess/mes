#!/usr/bin/env python

"""QR Code encoder

All needed by the user is done via the QRCodeEncoder class:

>>> encoder = QRCodeEncoder("HuDoRa")
>>> # encoder.save( "test.png" )
>>> print encoder.get_ascii()

"""

__revision__ = "$Rev$"

from textencoder import TextEncoder
from renderer import QRCodeRenderer


class QRCodeEncoder:
    """Top-level class which handles the overall process of
    encoding input data, placing it in the matrix and
    outputting the result"""

    def __init__(self, text, ecl=None):
        """Set up the encoder with the input text.
        This will encode the text,
        and create a matrix with the resulting codewords"""

        enc = TextEncoder()
        self.matrix = enc.encode(text, ecl)
        self.height = 0
        self.width = 0

    def save(self, filename, cellsize=5):
        """Write the matrix out to an image file"""

        qrc = QRCodeRenderer(self.matrix)
        qrc.write_file(cellsize, filename)

    def get_imagedata(self, cellsize=5):
        """Write the matrix out to a PNG bytestream"""

        qrc = QRCodeRenderer(self.matrix)
        imagedata = qrc.get_imagedata(cellsize)
        self.height = qrc.mtx_size
        self.width = qrc.mtx_size
        return imagedata

    def get_ascii(self):
        """Return an ascii representation of the matrix"""
        qrc = QRCodeRenderer(self.matrix)
        return qrc.get_ascii()
