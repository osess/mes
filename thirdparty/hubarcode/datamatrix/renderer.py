"""Datamatrix renderer"""

__revision__ = "$Rev$"

from cStringIO import StringIO
from PIL import Image


class DataMatrixRenderer:
    """Rendering class - given a pre-populated datamatrix.
    it will add edge handles and render to either to an image
    (including quiet zone) or ascii printout"""

    def __init__(self, matrix):
        self.width = len(matrix)
        self.height = len(matrix[0])

        self.matrix = matrix

        # grow the matrix in preparation for the handles
        self.add_border(colour=0)

        # add the edge handles
        self.add_handles()

    def put_cell(self, (posx, posy), colour=1):
        """Set the contents of the given cell"""

        self.matrix[posy][posx] = colour

    def add_handles(self):
        """Set up the edge handles"""
        # bottom solid border
        for posx in range(0, self.width):
            self.put_cell((posx, self.height - 1))

        # left solid border
        for posy in range(0, self.height):
            self.put_cell((0, posy))

        # top broken border
        for i in range(0, self.width - 1, 2):
            self.put_cell((i, 0))

        # right broken border
        for i in range(self.height - 1, 0, -2):
            self.put_cell((self.width - 1, i))

    def add_border(self, colour=1, width=1):
        """Wrap the matrix in a border of given width
            and colour"""

        self.width += (width * 2)
        self.height += (width * 2)

        self.matrix = \
            [[colour] * self.width] * width + \
            [[colour] * width + self.matrix[i] + [colour] * width
                for i in range(0, self.height - (width * 2))] + \
            [[colour] * self.width] * width

    def get_pilimage(self, cellsize):
        """Return the matrix as an PIL object"""

        # add the quiet zone (2 x cell width)
        self.add_border(colour=0, width=2)

        # get the matrix into the right buffer format
        buff = self.get_buffer(cellsize)

        # write the buffer out to an image
        img = Image.frombuffer('L',
                               (self.width * cellsize, self.height * cellsize),
                               buff, 'raw', 'L', 0, -1)
        return img

    def write_file(self, cellsize, filename):
        """Write the matrix out to an image file"""
        img = self.get_pilimage(cellsize)
        img.save(filename)

    def get_imagedata(self, cellsize):
        """Write the matrix out as PNG to an bytestream"""
        imagedata = StringIO()
        img = self.get_pilimage(cellsize)
        img.save(imagedata, "PNG")
        return imagedata.getvalue()

    def get_buffer(self, cellsize):
        """Convert the matrix into the buffer format used by PIL"""

        def pixel(value):
            """return pixel representation of a matrix value
            0 => white, 1 => black"""
            if value == 0:
                return chr(255)
            elif value == 1:
                return chr(0)

        # PIL writes image buffers from the bottom up,
        # so feed in the rows in reverse
        buf = ""
        for row in self.matrix[::-1]:
            bufrow = ''.join([pixel(cell) * cellsize for cell in row])
            for _ in range(0, cellsize):
                buf += bufrow
        return buf

    def get_ascii(self):
        """Write an ascii version of the matrix out to screen"""

        def symbol(value):
            """return ascii representation of matrix value"""
            if value == 0:
                return '  '
            elif value == 1:
                return 'XX'

        return '\n'.join([''.join([symbol(cell) for cell in row]) for row in self.matrix]) + '\n'
