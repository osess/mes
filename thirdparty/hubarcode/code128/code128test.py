"""Unit test for code128 barcode encoder"""


import unittest

from __init__ import Code128Encoder


class Code128Test(unittest.TestCase):
    """Unit test class for code128 bar code encoder"""

    test_strings = ("banana",
                    "wer das liest ist 31337",
                    "http://hudora.de/",
                    "http://hudora.de/artnr/12345/12/",
                    "http://hudora.de/track/00340059980000001319/",
                    "12345678",
                    "123456789"
                    )

    def test_charset_encoding(self):
        """Make sure the character set encoding, code type switching
        and optimization works correctly"""
        known_good = {
            # dense C encoding
            # immediate switch into C-mode, should compress
            "1234": [105, 12, 34],

            # B only
            "hello": [104, 72, 69, 76, 76, 79],

            # B switching to C
            "HI345678": [104, 40, 41, 99, 34, 56, 78],

            "BarCode 1": [104, 34, 65, 82, 35, 79, 68, 69, 0, 17],
        }
        for text, encoded in known_good.items():
            enc = Code128Encoder(text)
            self.assertEqual(enc.encoded_text, encoded)

        # B => C => B, with leftover digit
        self.assertEqual(Code128Encoder('HI34567A').encoded_text, [104, 40, 41, 99, 34, 56, 100, 23, 33])

        # there was a Bug in C encoding when we have a leftover digit at the end
        # see https://github.com/hudora/huBarcode/issues/issue/11
        self.assertEqual(Code128Encoder('12345').encoded_text, [105, 12, 34, 100, 21])

    def test_check_sum(self):
        """Make sure the checksum is calculated correctly"""

        known_good = {
            "HI345678": 68,
            "BarCode 1": 33
        }

        for text, chk in known_good.items():
            enc = Code128Encoder(text)
            self.assertEqual(enc.checksum, chk)

    def test_bar_encoding(self):
        """Make sure the bar encoding works correctly"""
        bars = "11010010000" + "11000101000" + "11000100010" + \
            "10111011110" + "10001011000" + "11100010110" + \
            "11000010100" + "10000100110" + "11000111010" + "11"

        text = "HI345678"

        enc = Code128Encoder(text)
        self.assertEqual(enc.bars, bars)

    def test_against_generated(self):
        """Compare the output of this library with generated barcodes"""

        for index, string in enumerate(Code128Test.test_strings):
            encoder = Code128Encoder(string)
            encoder.save('test.png')

            import filecmp
            self.failUnless(filecmp.cmp('test.png',
                            'hubarcode/code128/test_img/%d.png' % (index + 1)))


if __name__ == '__main__':
    unittest.main()
