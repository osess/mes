"""ISO/IEC 18004:2006 tables and functions implementation"""

import os.path

MAX_DATA_BITS = [
    128, 224, 352, 512, 688, 864, 992, 1232, 1456, 1728,
    2032, 2320, 2672, 2920, 3320, 3624, 4056, 4504, 5016, 5352,
    5712, 6256, 6880, 7312, 8000, 8496, 9024, 9544, 10136, 10984,
    11640, 12328, 13048, 13800, 14496, 15312, 15936, 16816, 17728, 18672,

    152, 272, 440, 640, 864, 1088, 1248, 1552, 1856, 2192,
    2592, 2960, 3424, 3688, 4184, 4712, 5176, 5768, 6360, 6888,
    7456, 8048, 8752, 9392, 10208, 10960, 11744, 12248, 13048, 13880,
    14744, 15640, 16568, 17528, 18448, 19472, 20528, 21616, 22496, 23648,

    72, 128, 208, 288, 368, 480, 528, 688, 800, 976,
    1120, 1264, 1440, 1576, 1784, 2024, 2264, 2504, 2728, 3080,
    3248, 3536, 3712, 4112, 4304, 4768, 5024, 5288, 5608, 5960,
    6344, 6760, 7208, 7688, 7888, 8432, 8768, 9136, 9776, 10208,

    104, 176, 272, 384, 496, 608, 704, 880, 1056, 1232,
    1440, 1648, 1952, 2088, 2360, 2600, 2936, 3176, 3560, 3880,
    4096, 4544, 4912, 5312, 5744, 6032, 6464, 6968, 7288, 7880,
    8264, 8920, 9368, 9848, 10288, 10832, 11408, 12016, 12656, 13328]


MAX_CODEWORDS = [
    0, 26, 44, 70, 100, 134, 172, 196, 242,
    292, 346, 404, 466, 532, 581, 655, 733, 815, 901, 991, 1085, 1156,
    1258, 1364, 1474, 1588, 1706, 1828, 1921, 2051, 2185, 2323, 2465,
    2611, 2761, 2876, 3034, 3196, 3362, 3532, 3706]


MATRIX_REMAIN_BIT = [0, 0, 7, 7, 7, 7, 7, 0,
                     0, 0, 0, 0, 0, 0, 3, 3,
                     3, 3, 3, 3, 3, 4, 4, 4,
                     4, 4, 4, 4, 3, 3, 3, 3,
                     3, 3, 3, 0, 0, 0, 0, 0, 0]


class MatrixInfo:
    """ Provides QR Code version and Error Correction Level
    dependent information necessary for creating matrix"""

    def __init__(self, version, ecl):
        path = os.path.join(os.path.split(__file__)[0], 'qrcode_data')

        self.byte_num = (MATRIX_REMAIN_BIT[version] + (MAX_CODEWORDS[version] << 3))

        filename = path + "/qrv" + str(version) + "_"
        filename += str(ecl) + ".dat"
        fhndl = open(filename, "rb")
        unpack = lambda y: [ord(x) for x in y]
        self.matrix_d = []
        self.matrix_d.append(unpack(fhndl.read(self.byte_num)))
        self.matrix_d.append(unpack(fhndl.read(self.byte_num)))
        self.matrix_d.append(unpack(fhndl.read(self.byte_num)))
        self.format_info = []
        self.format_info.append(unpack(fhndl.read(15)))
        self.format_info.append(unpack(fhndl.read(15)))
        self.rs_ecc_codewords = ord(fhndl.read(1))
        self.rs_block_order = unpack(fhndl.read(128))
        fhndl.close()

        filename = path + "/rsc" + str(self.rs_ecc_codewords) + ".dat"

        fhndl = open(filename, "rb")

        self.rs_cal_table = []

        for _ in range(0, 256):
            self.rs_cal_table.append(unpack(fhndl.read(self.rs_ecc_codewords)))
        # end for
        fhndl.close()

        filename = path + "/qrvfr" + str(version) + ".dat"
        fhndl = open(filename, "rb")
        frame_data_str = fhndl.read(65535)
        self.frame_data = []
        for line in frame_data_str.split("\n"):
            frame_line = []
            for char in line:
                if char == '1':
                    frame_line.append(1)
                elif char == '0':
                    frame_line.append(0)
                else:
                    raise ValueError("Corrupted frame data file")
                # end if
            # end for
            self.frame_data.append(frame_line)
        # end for
        fhndl.close()
    # end def __init__

    def create_matrix(self, version, codewords):
        """Create matrix based on version and fills it w/ codewords"""

        mtx_size = 17 + (version << 2)
        matrix = [[0 for i in range(mtx_size)] for j in range(mtx_size)]

        max_codewords = MAX_CODEWORDS[version]
        i = 0
        while i < max_codewords:
            codeword_i = codewords[i]
            j = 7
            while j >= 0:
                codeword_bits_number = (i << 3) + j
                pos_x = self.matrix_d[0][codeword_bits_number]
                pos_y = self.matrix_d[1][codeword_bits_number]
                mask = self.matrix_d[2][codeword_bits_number]
                matrix[pos_x][pos_y] = ((255 * (codeword_i & 1)) ^ mask)
                codeword_i = codeword_i >> 1
                j -= 1
            # end while
            i += 1
        # end while

        for matrix_remain in range(MATRIX_REMAIN_BIT[version], 0, -1):
            remain_bit_temp = matrix_remain + (max_codewords << 3) - 1
            pos_x = self.matrix_d[0][remain_bit_temp]
            pos_y = self.matrix_d[1][remain_bit_temp]
            mask = self.matrix_d[2][remain_bit_temp]
            matrix[pos_x][pos_y] = (255 ^ mask)
        # end for
        return matrix
    # end def create_matrix

    def put_format_info(self, matrix, format_info_value):
        """Put format information into the matrix"""

        format_info = ["101010000010010", "101000100100101",
                       "101111001111100", "101101101001011",
                       "100010111111001", "100000011001110",
                       "100111110010111", "100101010100000",
                       "111011111000100", "111001011110011",
                       "111110110101010", "111100010011101",
                       "110011000101111", "110001100011000",
                       "110110001000001", "110100101110110",
                       "001011010001001", "001001110111110",
                       "001110011100111", "001100111010000",
                       "000011101100010", "000001001010101",
                       "000110100001100", "000100000111011",
                       "011010101011111", "011000001101000",
                       "011111100110001", "011101000000110",
                       "010010010110100", "010000110000011",
                       "010111011011010", "010101111101101"]

        format_info_x1 = [0, 1, 2, 3, 4, 5, 7, 8, 8, 8, 8, 8, 8, 8, 8]
        format_info_y1 = [8, 8, 8, 8, 8, 8, 8, 8, 7, 5, 4, 3, 2, 1, 0]
        for i in range(15):
            content = int(format_info[format_info_value][i]) * 255
            matrix[format_info_x1[i]][format_info_y1[i]] = content
            matrix[self.format_info[0][i]][self.format_info[1][i]] = content
        # end for
    # end def put_format_info

    def finalize(self, matrix_content, mask_content):
        """Create final matrix and put frame data into it"""

        mtx_size = len(matrix_content)
        matrix = [[0 for i in range(mtx_size)] for j in range(mtx_size)]

        for i in range(mtx_size):
            for j in range(mtx_size):
                if (int(matrix_content[j][i]) & mask_content) != 0:
                    matrix[i][j] = 1
                else:
                    matrix[i][j] = self.frame_data[i][j]
                # end if
            # end for
        # end for
        return matrix
    # end def finalize

    def calc_demerit_score(self, bit_r, dem_data):
        """Calculate demerit score"""

        n1_search = (chr(255) * 5) + "+|" + (bit_r * 5) + "+"
        n3_search = bit_r + chr(255) + bit_r * 3 + chr(255) + bit_r

        import re
        demerit = [0, 0, 0, 0]
        demerit[2] = len(re.findall(n3_search, dem_data[0])) * 40
        demerit[3] = dem_data[1].count(bit_r) * len(bit_r) * 100
        demerit[3] /= self.byte_num
        demerit[3] -= 50
        demerit[3] = abs(int(demerit[3] / 5)) * 10

        ptn_temp = re.findall(bit_r + bit_r + "+", dem_data[2])
        demerit[1] += sum([len(x) - 1 for x in ptn_temp])

        ptn_temp = re.findall(chr(255) + chr(255) + "+", dem_data[3])
        demerit[1] += sum([len(x) - 1 for x in ptn_temp])
        demerit[1] *= 3

        ptn_temp = re.findall(n1_search, dem_data[0])
        demerit[0] += sum([len(x) - 2 for x in ptn_temp])
        return sum(demerit)
    # end def calc_demerit_score

    def calc_mask_number(self, matrix_content):
        """Calculate mask number for matrix"""

        mtx_size = len(matrix_content)
        mask_number = 0
        min_demerit_score = 0
        hor_master = ""
        ver_master = ""
        for i in range(0, mtx_size):
            for k in range(0, mtx_size):
                hor_master += chr(matrix_content[k][i])
                ver_master += chr(matrix_content[i][k])
            # end for
        # end for

        for i in range(0, 8):
            bit_r = chr((~(1 << i)) & 255)
            bit_mask = chr(1 << i) * mtx_size * mtx_size
            dem_data = ["", "", "", ""]
            dem_data[0] = strings_and(hor_master, bit_mask)
            dem_data[1] = strings_and(ver_master, bit_mask)
            dem_data[2] = strings_and(
                ((chr(170) * mtx_size) + dem_data[1]),
                (dem_data[1] + (chr(170) * mtx_size)))
            dem_data[3] = strings_or(
                ((chr(170) * mtx_size) + dem_data[1]),
                (dem_data[1] + (chr(170) * mtx_size)))
            dem_data = [string_not(x) for x in dem_data]

            str_split = lambda x, a: [x[p:p + a] for p in range(0, len(x), a)]
            dem_data = [chr(170).join(str_split(x, mtx_size)) for x in dem_data]

            dem_data[0] += chr(170) + dem_data[1]
            demerit_score = self.calc_demerit_score(bit_r, dem_data)
            if (demerit_score <= min_demerit_score or i == 0):
                mask_number = i
                min_demerit_score = demerit_score
            # end if
        # end for
        return mask_number
    # end def calc_mask_number
# end class MatrixInfo


def strings_and(str1, str2):
    """Apply logical 'and' to strings"""

    if (len(str1) < len(str2)):
        str1, str2 = str2, str1
    # end if
    str2 += '\0' * (len(str1) - len(str2))
    return "".join([chr(ord(x1) & ord(x2)) for x1, x2 in zip(str1, str2)])
# end def strings_and


def strings_or(str1, str2):
    """Apply logical 'or' to strings"""

    if (len(str1) < len(str2)):
        str1, str2 = str2, str1
    # end if
    str2 += '\0' * (len(str1) - len(str2))
    return "".join([chr(ord(x1) | ord(x2)) for x1, x2 in zip(str1, str2)])
# end def strings_or


def string_not(str1):
    """Apply logical 'not' to every symbol of string"""

    return "".join([chr(256 + ~ord(x)) for x in str1])
# end def string_not
