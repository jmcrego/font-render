from PIL import Image, ImageDraw, ImageFont

class GlyphRenderer:
    def __init__(self, font_path="fonts/unifont-16.0.04.ttf", cell_size=16, max_cols=16, img_mode="L"):
        """
        Render tokens into a single-row sequence of characters.
        Args:
            font_path: Path to monospaced TTF font.
            cell_size: Size of each character cell (square).
            max_cols: Maximum number of characters (columns).
            img_mode: 'L' for grayscale, '1' for binary, 'RGB' for color.
        """
        self.font_path = font_path
        self.cell_size = cell_size
        self.max_cols = max_cols
        self.img_mode = img_mode
        # Load font
        self.font = ImageFont.truetype(font_path, cell_size)
        self.cache_char2img = {}

    def render_char(self, ch):
        """
        Render a single character into a cell_size x cell_size image with caching.
        """
        if ch in self.cache_char2img:
            return self.cache_char2img[ch]
        
        img = Image.new(self.img_mode, (self.cell_size, self.cell_size), 0)
        draw = ImageDraw.Draw(img)

        # Get glyph bounding box
        bbox = self.font.getbbox(ch)  # (x0, y0, x1, y1)
        char_w = bbox[2] - bbox[0]
        char_h = bbox[3] - bbox[1]

        # Align top-left of glyph with cell top-left
        x = -bbox[0]   # shift left if bbox.x0 != 0
        y = -bbox[1]   # shift up if bbox.y0 != 0

        draw.text((x, y), ch, fill=255, font=self.font)
        self.cache_char2img[ch] = img

        # draw.text((0, 0), ch, fill=255, font=self.font)
        # self.cache_char2img[ch] = img
        return img

    def render_token(self, token):
        """
        Render all characters of a token in a single row.
        Always returns an image of size (cell_size, cell_size * max_cols).
        If the token is longer than max_cols, truncate it.
        Shorter tokens are right-padded with blank space.
        """
        token = token[:self.max_cols]
        num_chars = len(token)

        # Fixed canvas size (always same width)
        width = self.cell_size * self.max_cols
        height = self.cell_size
        img = Image.new(self.img_mode, (width, height), 0)

        # Paste each character sequentially
        for i, ch in enumerate(token):
            char_img = self.render_char(ch)
            img.paste(char_img, (i * self.cell_size, 0))
        return img

    def __call__(self, t):
        """
        Render a list of strings (tokens) or a single string (token).
        """
        if type(t) is list:
            return [self.render_token(x) for x in t]
        return self.render_token(t)

if __name__ == "__main__":

    renderer = GlyphRenderer()
    img = renderer("▁,;'.-_漢")
    img.show()
