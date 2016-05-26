"""Text encoder for code128 barcode encoder"""

import logging
log = logging.getLogger("code128")


import encoding

START_A, START_B, START_C = 103, 104, 105
TO_C, TO_B, TO_A = 99, 100, 101

start_codes = {
    'A': START_A,
    'B': START_B,
    'C': START_C
}

to_values = {
    TO_A: START_A,
    TO_B: START_B,
    TO_C: START_C
}


class TextEncoder:
    """Class which encodes a raw text string into a list of
    character codes.
    Adds in character set switch codes, and compresses pairs of
    digits under character set C"""

    def __init__(self):
        self.current_charset = 'B'
        self.digits = ""

    def switch_charset(self, new_charset):
        """Switch to a new character set
        Return a single item list containing the switch code"""

        log.debug("Switching charsets from %c to %c",
                  self.current_charset, new_charset)

        if new_charset == 'A':
            switch_code = self.convert_char('TO_A')
        elif new_charset == 'B':
            switch_code = self.convert_char('TO_B')
        elif new_charset == 'C':
            switch_code = self.convert_char('TO_C')

        self.current_charset = new_charset

        return [switch_code, ]

    def switch_charset_if_necessary(self, char, lookahead):
        """Decide whether we want to switch charsets for the
        next character"""

        def upcoming_digits():
            """Return true if there are more than three consecutive digits
            coming up"""
            num_digits = 0
            for char in lookahead:
                if char.isdigit():
                    num_digits += 1
                else:
                    break

            return num_digits > 3

        codes = []
        if self.current_charset == 'C' and not char.isdigit():
            # Switch from C - the next char is not a digit

            # by default, switch to B
            if char in encoding.charset_b.keys():
                codes = self.switch_charset('B')

            # but if the character's not in B, switch to A
            elif char in encoding.charset_a.keys():
                codes = self.switch_charset('A')

            else:
                log.error("No charset found for character %d" % ord(char))

             # Take care of the odd leftover digit if there is one
            if len(self.digits) == 1:
                codes.append(self.convert_char(self.digits[0]))
                self.digits = ''

        elif self.current_charset == 'B':
            # Do we want to switch from B?

            # Lookahead - are there lots of digits coming up?
            # If so, switch to C
            if upcoming_digits():
                codes = self.switch_charset('C')

            # If B can't handle the next char, switch to A
            elif char not in encoding.charset_b.keys():
                if char in encoding.charset_a.keys():
                    codes = self.switch_charset('A')
                else:
                    log.error("No charset found for character %d" % ord(char))

        elif self.current_charset == 'A':
            # Do we want to switch from A?

            # Lookahead - are there lots of digits coming up?
            # If so, switch to C
            if upcoming_digits():
                codes = self.switch_charset('C')

            # If A can't handle the next char, switch to B
            elif char not in encoding.charset_a.keys():
                if char in encoding.charset_b.keys():
                    codes = self.switch_charset('B')
                else:
                    log.error("No charset found for character %d" % ord(char))

        return codes

    def convert_char(self, char):
        """Convert the given character into the current charset
        For A and B and a few cases in C, this is a simple lookup in
        the charset table.
        For most cases in C, this involves grouping consecutive digits
        into pairs and adding in each pair as a single character"""

        if self.current_charset == 'A':
            return encoding.charset_a[char]

        elif self.current_charset == 'B':
            return encoding.charset_b[char]

        elif self.current_charset == 'C':
            if char in encoding.charset_c.keys():
                return encoding.charset_c[char]
            elif char.isdigit():
                # store char in the digit buffer
                # and append when there are two digits stored
                self.digits += char
                if len(self.digits) == 2:
                    ret = int(self.digits)
                    self.digits = ""
                    return ret

    def optimize_encoding(self, enc):
        """Perform various optimizations on the encoded string"""

        # [START_X, TO_Y]  => [START_Y,]
        # (This is only relevant at the start)
        # Saves one character
        if enc[1] in to_values.keys():
            enc[0:2] = [to_values[enc[1]]]
        # [START_X, FNC1, TO_Y]  => [START_Y, FNC1, ]
        elif enc[1] == 102 and enc[2] in to_values.keys():
            enc[0:3] = [to_values[enc[2]], 102]

    def encode(self, text):
        """Encode the given text, optimize it and return a
        list of character codes"""

        encoded_text = []

        # First symbol is always the start code for the initial charset
        encoded_text.append(start_codes[self.current_charset])

        # Start with charset B
        for i, char in enumerate(text):
            encoded_text.extend(self.switch_charset_if_necessary(
                char, text[i:i + 10]))
            converted = self.convert_char(char)
            if converted is not None:
                encoded_text.append(converted)

        # Finale Take care of the odd leftover digit if there is
        # one from encoding Charset C
        if len(self.digits) == 1:
            # We now force Charset B
            encoded_text.extend(self.switch_charset('B'))
            encoded_text.append(self.convert_char(self.digits[0]))

        self.optimize_encoding(encoded_text)
        return encoded_text

    def get_bars(self, encoded_text, checksum):
        """Return the bar encoding (a string of ones and zeroes)
        representing the given encoded text and checksum digit.
        Stop code and termination bars are added onto the end"""

        full_code = encoded_text + [checksum, ]
        bars = ""
        for char in full_code:
            bars += encoding.encodings[char]

        bars += encoding.STOP
        bars += "11"

        return bars
