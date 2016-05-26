"""Code-128 barcode encoder

All needed by the user is done via the Code128Encoder class:

>>> encoder = Code128Encoder("HuDoRa")
>>> encoder.save("test.png")

Implemented by Helen Taylor for HUDORA GmbH.

Detailed documentation on the format here:
http://www.barcodeisland.com/code128.phtml
http://www.adams1.com/pub/russadam/128code.html

You may use this under a BSD License.
"""
from textencoder import TextEncoder
from renderer import Code128Renderer
import logging

log = logging.getLogger("code128")


class Code128Encoder:
    """Top-level class which handles the overall process of
    encoding input string and outputting the result"""

    def __init__(self, text, options=None):
        """ The options hash currently supports three options:
            * ttf_font: absolute path to a truetype font file used to render the label
            * ttf_fontsize: the size the label is drawn in
            * label_border: number of pixels space between the barcode and the label
            * bottom_border: number of pixels space between the label and the bottom border
            * height: height of the image in pixels """

        self.options = options
        self.text = text
        self.height = 0
        self.width = 0
        encoder = TextEncoder()

        self.encoded_text = encoder.encode(self.text)
        log.debug("Encoded text is %s", self.encoded_text)

        self.checksum = self.calculate_check_sum()
        log.debug("Checksum is %d", self.checksum)

        self.bars = encoder.get_bars(self.encoded_text, self.checksum)
        log.debug("Bars: %s", self.bars)

    def calculate_check_sum(self):
        """Calculate the check sum of the encoded text.
        Checksum is based on the input text and the starting code,
        and a mod103 algorithm is used"""

        checksum = self.encoded_text[0]

        for index, char in enumerate(self.encoded_text):
            if index > 0:
                checksum += (index * char)

        return checksum % 103

    def get_imagedata(self, bar_width=3):
        """Write the matrix out to an PNG bytestream"""

        barcode = Code128Renderer(self.bars, self.text, self.options)
        imagedata = barcode.get_imagedata(bar_width)
        self.width = barcode.image_width
        self.height = barcode.image_height
        return imagedata

    def save(self, filename, bar_width=3):
        """Write the barcode out to an image file"""
        Code128Renderer(
            self.bars, self.text, self.options).write_file(filename, bar_width)

        
