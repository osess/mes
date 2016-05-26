"""Rendering code for code128 barcode"""
from cStringIO import StringIO
from PIL import Image, ImageFont, ImageDraw
import logging
import os

log = logging.getLogger("code128")

# maps bar width against font size
FONT_SIZES = {
    1: 8,
    2: 14,
    3: 18,
    4: 24
}


class Code128Renderer:
    """Rendering class for code128 - given the bars and the original
    text, it will render an image of the barcode, including edge
    zones and text."""

    def __init__(self, bars, text, options=None):
        """ The options hash currently supports three options:
            * ttf_font: absolute path to a truetype font file used to render the label
            * ttf_fontsize: the size the label is drawn in
            * label_border: number of pixels space between the barcode and the label
            * bottom_border: number of pixels space between the label and the bottom border
            * height: height of the image in pixels
            * show_label: whether to show the label below the barcode (defaults to True) """
        self.options = options or {}
        self.bars = bars
        self.text = text
        self.image_width = None
        self.image_height = None

    def get_pilimage(self, bar_width):
        """Return the barcode as a PIL object"""

        show_label = self.options.get('show_label', True)

        # 11 bars per character, plus the stop
        num_bars = len(self.bars)

        log.debug("There are %d bars", num_bars)

        # Quiet zone is 10 bar widths on each side
        quiet_width = bar_width * 10

        fontsize = 0
        if show_label:
            default_fontsize = FONT_SIZES.get(bar_width, 24)
            fontsize = self.options.get('ttf_fontsize', default_fontsize)
            ttf_font = self.options.get('ttf_font')
            if ttf_font:
                font = ImageFont.truetype(ttf_font, fontsize)
            else:
                # Locate and load the font file relative to the module
                c128dir, _ = os.path.split(__file__)
                rootdir, _ = os.path.split(c128dir)

                fontfile = os.path.join(
                    rootdir, "fonts", "courR%02d.pil" % fontsize)
                font = ImageFont.load_path(fontfile)

        # Total image width
        self.image_width = (2 * quiet_width) + (num_bars * bar_width)

        # Image height 30% of width
        label_border = self.options.get('label_border', 0)
        self.image_height = self.options.get('height') or (self.image_width / 3)
        bar_height = self.image_height - label_border - fontsize

        # Image: has a white background
        bottom_border = self.options.get('bottom_border', 0)
        img = Image.new('L', (
            self.image_width, self.image_height + bottom_border), 255)

        class BarWriter:
            """Class which moves across the image, writing out bars"""
            def __init__(self, img, bar_height):
                self.img = img
                self.current_x = quiet_width
                if show_label:
                    self.symbol_top = quiet_width / 2
                else:
                    self.symbol_top = 0
                self.bar_height = bar_height - 4 #'- 4' is added by lxy

            def write_bar(self, value):
                """Draw a bar at the current position,
                if the value is 1, otherwise move on silently"""

                # only write anything to the image if bar value is 1
                if value == 1:
                    for ypos in range(self.symbol_top, self.bar_height):
                        for xpos in range(self.current_x,
                                          self.current_x + bar_width):
                            img.putpixel((xpos, ypos), 0)
                self.current_x += bar_width

            def write_bars(self, bars):
                """write all bars to the image"""
                for bar in bars:
                    self.write_bar(int(bar))

        # draw the barcode bars themself
        writer = BarWriter(img, bar_height)
        writer.write_bars(self.bars)

        # Draw the text
        draw = ImageDraw.Draw(img)
        if show_label:
            xtextwidth = font.getsize(self.text)[0]
            xtextpos = self.image_width / 2 - (xtextwidth / 2)
            ytextpos = bar_height + label_border - 5 #'- 5' is added by lxy
            draw.text((xtextpos, ytextpos), self.text, font=font)
        return img

    def write_file(self, filename, bar_width):
        """Write barcode data out to image file
        filename - the name of the image file or an file object
        bar_width - the desired width in pixels of each bar"""
        img = self.get_pilimage(bar_width)
        img.save(filename, 'PNG')

    def get_imagedata(self, bar_width):
        """Write the matrix out as PNG to an bytestream"""
        imagedata = StringIO()
        img = self.get_pilimage(bar_width)
        img.save(imagedata, "PNG")
        return imagedata.getvalue()
