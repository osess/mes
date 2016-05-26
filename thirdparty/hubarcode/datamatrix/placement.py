"""Matrix placement for 2D datamatrix barcode encoder"""
__revision__ = "$Rev$"


class DataMatrixPlacer:
    """Class which takes care of placing codewords in the correct position
    in the 2D datamatrix"""

    def __init__(self):
        """Initialize with an empty matrix"""
        self.matrix = None
        self.rows = 0
        self.cols = 0

    def place_bit(self, (posx, posy), bit):
        """Place bit in the correct location in the matrix"""

        # If out of bounds, wrap around to the other side
        if posx < 0:
            posx += self.rows
            posy += (4 - ((self.rows + 4) % 8))

        if posy < 0:
            posy += self.cols
            posx += (4 - ((self.cols + 4) % 8))

        self.matrix[posx][posy] = bit

    def place_special_1(self, codeword):
        """Special corner case 1
            bottom left corner: |1|2|3|

            top right corner:   |4|5|
                                  |6|
                                  |7|
                                  |8| """

        self.place_bit((self.rows - 1, 0), (codeword & (0x01 << 7)) >> 7)
        self.place_bit((self.rows - 1, 1), (codeword & (0x01 << 6)) >> 6)
        self.place_bit((self.rows - 1, 2), (codeword & (0x01 << 5)) >> 5)
        self.place_bit((0, self.cols - 2), (codeword & (0x01 << 4)) >> 4)
        self.place_bit((0, self.cols - 1), (codeword & (0x01 << 3)) >> 3)
        self.place_bit((1, self.cols - 1), (codeword & (0x01 << 2)) >> 2)
        self.place_bit((2, self.cols - 1), (codeword & (0x01 << 1)) >> 1)
        self.place_bit((3, self.cols - 1), codeword & 0x01)

    def place_special_2(self, codeword):
        """Special corner case 2
            bottom left corner: |1|
                                |2|
                                |3|

            top right corner:  |4|5|6|7|
                                     |8| """

        self.place_bit((self.rows - 3, 0), (codeword & (0x01 << 7)) >> 7)
        self.place_bit((self.rows - 2, 0), (codeword & (0x01 << 6)) >> 6)
        self.place_bit((self.rows - 1, 0), (codeword & (0x01 << 5)) >> 5)
        self.place_bit((0, self.cols - 4), (codeword & (0x01 << 4)) >> 4)
        self.place_bit((0, self.cols - 3), (codeword & (0x01 << 3)) >> 3)
        self.place_bit((0, self.cols - 2), (codeword & (0x01 << 2)) >> 2)
        self.place_bit((0, self.cols - 1), (codeword & (0x01 << 1)) >> 1)
        self.place_bit((1, self.cols - 1), codeword & 0x01)

    def place_special_3(self, codeword):
        """Special corner case 3
            bottom left corner: |1|
                                |2|
                                |3|

            top right corner:   |4|5|
                                  |6|
                                  |7|
                                  |8| """

        self.place_bit((self.rows - 3, 0), (codeword & (0x01 << 7)) >> 7)
        self.place_bit((self.rows - 2, 0), (codeword & (0x01 << 6)) >> 6)
        self.place_bit((self.rows - 1, 0), (codeword & (0x01 << 5)) >> 5)
        self.place_bit((0, self.cols - 2), (codeword & (0x01 << 4)) >> 4)
        self.place_bit((0, self.cols - 1), (codeword & (0x01 << 3)) >> 3)
        self.place_bit((1, self.cols - 1), (codeword & (0x01 << 2)) >> 2)
        self.place_bit((2, self.cols - 1), (codeword & (0x01 << 1)) >> 1)
        self.place_bit((3, self.cols - 1), codeword & 0x01)

    def place_special_4(self, codeword):
        """Special corner case 4
            bottom left corner: |1|

            bottom right corner: |2|

            top right corner: |3|4|5|
                              |6|7|8| """

        self.place_bit((self.rows - 1, 0), (codeword & (0x01 << 7)) >> 7)
        self.place_bit((self.rows - 1, self.cols - 1),
                       (codeword & (0x01 << 6)) >> 6)
        self.place_bit((0, self.cols - 3), (codeword & (0x01 << 5)) >> 5)
        self.place_bit((0, self.cols - 2), (codeword & (0x01 << 4)) >> 4)
        self.place_bit((0, self.cols - 1), (codeword & (0x01 << 3)) >> 3)
        self.place_bit((1, self.cols - 3), (codeword & (0x01 << 2)) >> 2)
        self.place_bit((1, self.cols - 2), (codeword & (0x01 << 1)) >> 1)
        self.place_bit((1, self.cols - 1), codeword & 0x01)

    def place_standard_shape(self, (posx, posy), codeword):
        """Standard codeword placement
            |1|2|
            |3|4|5|
            |6|7|8| """

        if self.matrix[posx][posy] is None:
            self.place_bit((posx - 2, posy - 2), (codeword & (0x01 << 7)) >> 7)
            self.place_bit((posx - 2, posy - 1), (codeword & (0x01 << 6)) >> 6)
            self.place_bit((posx - 1, posy - 2), (codeword & (0x01 << 5)) >> 5)
            self.place_bit((posx - 1, posy - 1), (codeword & (0x01 << 4)) >> 4)
            self.place_bit((posx - 1, posy - 0), (codeword & (0x01 << 3)) >> 3)
            self.place_bit((posx, posy - 2), (codeword & (0x01 << 2)) >> 2)
            self.place_bit((posx, posy - 1), (codeword & (0x01 << 1)) >> 1)
            self.place_bit((posx, posy - 0), (codeword & 0x01))

    def place(self, codewords, matrix):
        """Place all the given codewords into the given matrix
        Matrix should be correctly pre-sized"""

        self.matrix = matrix
        self.rows = len(matrix)
        self.cols = len(matrix[0])

        row, col = 4, 0

        cw_list = [ord(codeword) for codeword in codewords]

        while True:

            # Special corner cases
            if row == self.rows and col == 0:
                self.place_special_1(cw_list.pop(0))

            elif row == self.rows - 2 and col == 0 and self.cols % 4:
                self.place_special_2(cw_list.pop(0))

            elif row == self.rows - 2 and col == 0 and (self.cols % 8 == 4):
                self.place_special_3(cw_list.pop(0))

            elif row == self.rows + 4 and col == 2 and (self.cols % 8 == 0):
                self.place_special_4(cw_list.pop(0))

            # Sweep upwards diagonally
            while True:
                if row < self.rows and col >= 0 and self.matrix[row][col] is None:
                    self.place_standard_shape((row, col), cw_list.pop(0))

                row -= 2
                col += 2

                if row < 0 or col >= self.cols:
                    break

            row += 1
            col += 3

            # Sweep downwards diagonally
            while True:
                if row >= 0 and col < self.cols and self.matrix[row][col] is None:
                    self.place_standard_shape((row, col), cw_list.pop(0))

                row += 2
                col -= 2

                if row >= self.rows or col < 0:
                    break

            row += 3
            col += 1

            if row >= self.rows and col >= self.cols:
                break

        # Fill in any remaining Nones
        for row in self.matrix:
            for i in range(len(row)):
                if row[i] is None:
                    row[i] = 0
