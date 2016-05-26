"""Unit test for EAN-13 barcode encoder"""

import unittest

from __init__ import EAN13Encoder


class EAN13Test(unittest.TestCase):
    """Unit test class for EAN13 bar code encoder"""

    test_strings = ("012345678901",
                    "007567816412",
                    "750103131130")

    def test_check_digit(self):
        """Make sure the check digit calculation works"""

        # test includes the full range of check digits
        check_digits = {"012345678901": 2,
                        "007567816412": 5,
                        "750103131130": 9,
                        "000000000000": 0,
                        "000000010101": 1,
                        "000000001111": 2,
                        "000000000111": 3,
                        "000000000101": 4,
                        "000000001011": 5,
                        "000000001001": 6,
                        "000000000001": 7,
                        "000000001010": 8,
                        "000000000010": 9}
        for code, check in check_digits.items():
            enc = EAN13Encoder(code)
            self.assertEqual(enc.check_digit, check)

    def test_parity(self):
        """Test the parity calculations"""
        enc = EAN13Encoder("750103131130")
        self.assertEqual(enc.get_parity(), (1, 0, 1, 0, 1, 0))

    def test_encoding(self):
        """Make the the left and right encodings work"""
        enc = EAN13Encoder("750103131130")
        left, right = enc.encode()
        self.assertEqual(left, "011000101001110011001010011101111010110011")
        self.assertEqual(right, "100001011001101100110100001011100101110100")

    def test_against_generated(self):
        """Compare the output of this library with generated barcodes"""

        for index, string in enumerate(EAN13Test.test_strings):
            encoder = EAN13Encoder(string)
            encoder.save('test.png')

            import filecmp
            self.failUnless(filecmp.cmp('test.png',
                            'hubarcode/ean13/test_img/%d.png' % (index + 1)))


if __name__ == '__main__':
    unittest.main()
