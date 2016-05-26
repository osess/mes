"""Unit test for 2D datamatrix barcode encoder"""

__revision__ = "$Rev$"

import unittest
import os

from __init__ import DataMatrixEncoder

dmtxread_path = "dmtxread"
dmtxwrite_path = "dmtxwrite"


class MatrixTest(unittest.TestCase):
    """Unit test class for 2D datamatrix encoder"""

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
                    "http://www.hudora.de/track/0034",
                    )

    def test_encode_decode(self):
        """Test that dmtxwrite can decode this library's output
        to the correct string"""

        for string in MatrixTest.test_strings:

            encoder = DataMatrixEncoder(string)
            encoder.save("datamatrix-test.png")

            if not (os.path.exists(os.path.join('/usr/bin', dmtxread_path))
                    or os.path.exists(os.path.join('/usr/local/bin', dmtxread_path))):
                print "%r does not exist, skipping decoding tests" % dmtxread_path
            else:
                fin = os.popen("sh -c '%s datamatrix-test.png'" % (dmtxread_path))
                self.assertEqual(fin.readline(), string)

    def test_against_dmtx(self):
        """Compare the output of this library with that of dmtxwrite"""

        for string in MatrixTest.test_strings:
            encoder = DataMatrixEncoder(string)
            mine = encoder.get_ascii()

            if not os.path.exists(dmtxwrite_path):
                print "%r does not exist, skipping encoding tests" % dmtxwrite_path
            else:
                fin = os.popen("%s '%s'" % (dmtxwrite_path, string))
                output = ""
                while True:
                    line = fin.readline()
                    if not line:
                        break
                    if line[0] == 'X':
                        output += line
                self.assertEqual(output, mine)

    def test_encoding(self):
        """Test that text is correctly encoded, and also that padding
        and error codewords are correctly added"""

        correct_encodings = {
            "hi": [105, 106, 129, 74, 235, 130, 61, 159],
            "banana": [99, 98, 111, 98, 111, 98, 129, 56,
                       227, 236, 237, 109, 16, 221, 163, 60, 171, 76],
            "wer das liest ist 31337": [
                120, 102, 115, 33, 101, 98, 116, 33, 109, 106,
                102, 116, 117, 33, 106, 116, 117, 33, 161, 163,
                56, 129, 83, 116, 244, 3, 40, 16, 79, 220, 144,
                76, 17, 186, 175, 211, 244, 84, 59, 71]}
        from textencoder import TextEncoder
        enc = TextEncoder()
        for key, value in correct_encodings.items():
            self.assertEqual([ord(char) for char in enc.encode(key)], value)


if __name__ == '__main__':
    unittest.main()
