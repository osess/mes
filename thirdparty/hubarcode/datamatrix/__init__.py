#!/usr/bin/env python

"""2D Datamatrix barcode encoder

All needed by the user is done via the DataMatrixEncoder class:

>>> encoder = DataMatrixEncoder("HuDoRa")
>>> # encoder.save( "test.png" )
>>> print encoder.get_ascii()
XX  XX  XX  XX  XX  XX  XX
XX  XXXX  XXXXXX      XXXXXX
XXXXXX    XX          XX
XXXXXX    XX        XXXX  XX
XXXX  XX  XXXXXX
XXXXXX    XXXXXXXX    XXXXXX
XX    XX  XXXXXXXX  XXXX
XX    XX      XXXX      XXXX
XX  XXXXXXXXXX    XXXX
XX  XXXX    XX            XX
XX  XXXXXX  XXXXXX      XX
XXXXXX  XX  XX  XX  XX    XX
XX    XX              XX
XXXXXXXXXXXXXXXXXXXXXXXXXXXX


Implemented by Helen Taylor for HUDORA GmbH.

Detailed documentation on the format here:
http://grandzebu.net/informatique/codbar-en/datamatrix.htm
Further resources here: http://www.libdmtx.org/resources.php

You may use this under a BSD License.
"""

__revision__ = "$Rev$"

from textencoder import TextEncoder
from placement import DataMatrixPlacer
from renderer import DataMatrixRenderer


class DataMatrixEncoder:
    """Top-level class which handles the overall process of
    encoding input data, placing it in the matrix and
    outputting the result"""

    def __init__(self, text):
        """Set up the encoder with the input text.
        This will encode the text,
        and create a matrix with the resulting codewords"""

        enc = TextEncoder()
        codewords = enc.encode(text)
        self.width = 0
        self.height = 0
        matrix_size = enc.mtx_size

        self.matrix = [[None] * matrix_size for _ in range(0, matrix_size)]

        placer = DataMatrixPlacer()
        placer.place(codewords, self.matrix)

    def save(self, filename, cellsize=5):
        """Write the matrix out to an image file"""
        dmtx = DataMatrixRenderer(self.matrix)
        dmtx.write_file(cellsize, filename)

    def get_imagedata(self, cellsize=5):
        """Write the matrix out to an PNG bytestream"""
        dmtx = DataMatrixRenderer(self.matrix)
        self.width = dmtx.width
        self.height = dmtx.height
        return dmtx.get_imagedata(cellsize)

    def get_ascii(self):
        """Return an ascii representation of the matrix"""
        dmtx = DataMatrixRenderer(self.matrix)
        return dmtx.get_ascii()
