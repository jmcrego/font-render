from PIL import Image, ImageDraw, ImageFont

class GridGlyphRenderer:
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
        self.char_cache = {}

    def render_char(self, ch):
        """
        Render a single character into a cell_size x cell_size image with caching.
        """
        if ch in self.char_cache:
            return self.char_cache[ch]

        img = Image.new(self.img_mode, (self.cell_size, self.cell_size), 0)
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), ch, fill=255, font=self.font)
        self.char_cache[ch] = img
        return img

    def render_token(self, token):
        """
        Render all characters of a token in a single row.
        If the token is longer than max_cols, truncate it.
        """
        token = token[:self.max_cols]
        num_chars = len(token)
        # Create single-row canvas
        width = self.cell_size * num_chars
        height = self.cell_size
        img = Image.new(self.img_mode, (width, height), 0)
        # Paste each character sequentially
        for i, ch in enumerate(token):
            char_img = self.render_char(ch)
            img.paste(char_img, (i * self.cell_size, 0))

        return img

    def __call__(self, t):
        """
        render a list of strings (tokens) or a single string (token).
        """
        if type(t) is list:
            return [self.render_token(x) for x in t]
        return self.render_token(t)

if __name__ == "__main__":

    renderer = GridGlyphRenderer()
    img = renderer("▁@#%,;'.-_漢")
    img.show()




