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
        """Render a single character into a cell_size x cell_size image with caching."""
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


    def render_token2(self, token):
        """
        Compose up to n_rows x n_cols characters into a single image.
        If token has fewer characters than max, empty cells are left black.
        """
        max_chars = self.n_rows * self.n_cols
        token = token[:max_chars]

        img = Image.new(self.img_mode, (self.cell_size*self.n_cols, self.cell_size*self.n_rows), 0)

        for i, ch in enumerate(token):
            row = i // self.n_cols
            col = i % self.n_cols
            char_img = self.render_char(ch)
            img.paste(char_img, (col*self.cell_size, row*self.cell_size))

        return img

    def __call__(self, tokens):
        return [self.render_token(t) for t in tokens]


font_path = "fonts/NotoSansMono-VariableFont_wdth,wght.ttf"
font_path = "fonts/unifont-16.0.04.ttf"
renderer = GridGlyphRenderer(font_path, cell_size=128, max_cols=16)

img = renderer.render_token("▁@#%,;'.-_漢")
img.show()




