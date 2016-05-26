"""Encoding tables and functions for EAN-13 barcode"""

#
# Map the first number system digit to the parity encodings for the
# following fields, in order:
# second number system digit
# the five manufacturing code characters, in order
# 0 = even
# 1 = odd
#
parity_table = {
    0: (1, 1, 1, 1, 1, 1),
    1: (1, 1, 0, 1, 0, 0),
    2: (1, 1, 0, 0, 1, 0),
    3: (1, 1, 0, 0, 0, 1),
    4: (1, 0, 1, 1, 0, 0),
    5: (1, 0, 0, 1, 1, 0),
    6: (1, 0, 0, 0, 1, 1),
    7: (1, 0, 1, 0, 1, 0),
    8: (1, 0, 1, 0, 0, 1),
    9: (1, 0, 0, 1, 0, 1),
}

#
# How to encode different digits depending on parity and where
# they are in the code
# Values are for digits placed as follows:
# Left hand side, odd parity
# Left hand side, even parity
# Right hand side (all characters)
#
encoding_table = {
    0: ("0001101", "0100111", "1110010"),
    1: ("0011001", "0110011", "1100110"),
    2: ("0010011", "0011011", "1101100"),
    3: ("0111101", "0100001", "1000010"),
    4: ("0100011", "0011101", "1011100"),
    5: ("0110001", "0111001", "1001110"),
    6: ("0101111", "0000101", "1010000"),
    7: ("0111011", "0010001", "1000100"),
    8: ("0110111", "0001001", "1001000"),
    9: ("0001011", "0010111", "1110100"),
}


def get_left_encoded(digit, parity):
    """Get the left hand encoding of the given digit, under
    the given parity (0=even or 1=odd)"""

    if parity not in (0, 1):
        raise Exception("Invalid parity '%s'" % parity)
    elif digit not in list(range(0, 10)):
        raise Exception("Invalid digit '%s'" % digit)
    else:
        return encoding_table[digit][1 - parity]


def get_right_encoded(digit):
    """Get the right hand encoding of the given digit"""

    if digit not in list(range(0, 10)):
        raise Exception("Invalid digit '%s'" % digit)
    else:
        return encoding_table[digit][2]
