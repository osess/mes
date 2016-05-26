"""Unit test for QR Code barcode encoder"""

import unittest

from qrcode import QRCodeEncoder


class MatrixTest(unittest.TestCase):
    """Unit test class for QR Code encoder"""

    test_strings = ("banana",
                    "wer das liest ist 31337",
                    "http://hudora.de/",
                    "http://hudora.de/artnr/12345/12/",
                    "http://hudora.de/track/00340059980000001319/",
                    "http://www.hudora.de/track/00340059980000001319/",
                    "http://www.hudora.de/track/00340059980000001319",
                    "http://www.hudora.de/track/0034005998000000131",
                    "http://www.hudora.de/track/003400599800000013",
                    "http://www.hudora.de/track/00340059980000001",
                    "http://www.hudora.de/track/0034005998000000",
                    "http://www.hudora.de/track/003400599800000",
                    "http://www.hudora.de/track/00340059980000",
                    "http://www.hudora.de/track/0034005998000",
                    "http://www.hudora.de/track/003400599800",
                    "http://www.hudora.de/track/00340059980",
                    "http://www.hudora.de/track/0034005998",
                    "http://www.hudora.de/track/003400599",
                    "http://www.hudora.de/track/00340059",
                    "http://www.hudora.de/track/0034005",
                    "http://www.hudora.de/track/003400",
                    "http://www.hudora.de/track/00340",
                    "http://www.hudora.de/track/0034")

    def test_against_generated(self):
        """Compare the output of this library with generated barcodes"""

        i = 1
        for string in MatrixTest.test_strings:
            encoder = QRCodeEncoder(string, 'M')
            encoder.save('test.png', 3)

            import filecmp
            self.failUnless(filecmp.cmp('test.png',
                                        'hubarcode/qrcode/test_img/%d.png' % i))
            i += 1

    def test_encoding(self):
        """Test that text is correctly encoded, and also that padding
        and error codewords are correctly added"""

        correct_encodings = {
            "hi": [64, 38, 134, 144, 236, 17, 236, 17, 236, 17, 236,
                   17, 236, 17, 236, 17, 17, 160, 77, 193, 121, 155,
                   5, 133, 245, 218],

            "banana": [64, 102, 38, 22, 230, 22, 230, 16, 236, 17, 236,
                       17, 236, 17, 236, 17, 5, 142, 20, 56, 215, 125,
                       137, 131, 106, 125, 0],

            "wer das liest ist 31337": [
                65, 119, 118, 87, 34, 6, 70, 23, 50, 6, 198, 150,
                87, 55, 66, 6, 151, 55, 66, 3, 51, 19, 51, 51, 112,
                236, 17, 236, 124, 222, 181, 177, 208, 193, 45, 100,
                155, 47, 28, 28, 88, 55, 156, 59, 0, 0]}

        from qrcode.textencoder import TextEncoder
        enc = TextEncoder()
        for key, value in correct_encodings.items():
            enc.encode(key, ecl='M')
            self.assertEqual(enc.codewords, value)
