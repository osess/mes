"""EAN-13 barcode encoder

All needed by the user is done via the EAN13Encoder class:

>>> encoder = EAN13Encoder("012345678901")
>>> encoder.save("test.png")

Implemented by Helen Taylor for HUDORA GmbH.

Detailed documentation on the format here:
http://www.barcodeisland.com/ean13.phtml

You may use this under a BSD License.
"""

__revision__ = "$Rev: 1$"

import encoding
from renderer import EAN13Renderer
#handling movement of reduce to functools python >= 2.6
try:
    from functools import reduce
except ImportError:
    pass

GUARDS = ("101", "01010", "101")


class EAN13Encoder:
    """Top-level class which handles the overall process of
    encoding input number and outputting the result"""

    def __init__(self, code):
        """Set up the encoder with the concatenated input values.
        code must be 12 digits long in the following format
        nnmmmmmppppp
        where n is the number system
        m is the manufacturing code
        p is the product code"""

        # Make sure it's 12 digits long
        if len(code) == 13:
            # cut of check digit
            code = code[:-1]
        if code.isdigit() and len(code) == 12:
            self.code = code
            self.check_digit = self.calculate_check_digit()
            self.full_code = self.code + str(self.check_digit)
            self.left_bars = ""
            self.right_bars = ""
            self.height = 0
            self.width = 0
            self.encode()
        else:
            raise Exception("code must be 12 digits long")

    def encode(self):
        """Encode the barcode number and return the left and right
        data strings"""

        parity_values = self.get_parity()

        self.left_bars = ""
        self.right_bars = ""

        # Exclude the first number system digit, this was
        # for determining the left parity
        for parity, digit in zip(parity_values, self.full_code[1:7]):
            self.left_bars += encoding.get_left_encoded(int(digit), parity)
        for digit in self.full_code[7:]:
            self.right_bars += encoding.get_right_encoded(int(digit))

        return self.left_bars, self.right_bars

    def get_parity(self):
        """Return the parity mappings applicable to this code"""
        return encoding.parity_table[int(self.code[0])]

    def calculate_check_digit(self):
        """Modulo-10 calculation of the barcode check digit
        First, we take the rightmost digit of the value and consider it to be
        an "odd" character. We then move right-to-left, alternating between
        odd and even. We then sum the numeric value of all the even positions,
        and sum the numeric value multiplied by three of all the
        odd positions."""

        def sum_str(total, digit):
            """add a stringified digit to the total sum"""
            return total + int(digit)

        # sum the "odd" digits (1,3,5,7,9,11) and multiply by 3
        oddsum = reduce(sum_str, self.code[1::2], 0)

        # sum the "even" digits (0,2,4,6,8,10)
        evensum = reduce(sum_str, self.code[:12:2], 0)

        # add them up
        total = oddsum * 3 + evensum

        # check digit is the number that can be added to the total
        # to get to a multiple of 10
        return (10 - (total % 10)) % 10

    def get_imagedata(self, bar_width=3):
        """Write the barcode out to a PNG bytestream"""
        barcode = EAN13Renderer(
            self.full_code, self.left_bars, self.right_bars, GUARDS)
        imagedata = barcode.get_imagedata(bar_width)
        self.height = barcode.height
        self.width = barcode.width
        return imagedata

    def save(self, filename, bar_width=3):
        """Write the barcode out to an image file"""
        EAN13Renderer(self.full_code,
                      self.left_bars,
                      self.right_bars,
                      GUARDS).write_file(filename, bar_width)
