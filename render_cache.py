from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from fontTools.ttLib import TTFont


class GlyphCache:
    def __init__(self, font_path, font_size=32, img_mode="L", c=3, s=2, cache_dir=None):
        self.font_path = font_path
        self.font_size = font_size
        self.img_mode = img_mode #"L" means 8-bit grayscale (values 0–255). "RGB" would be a 3-channel color image. "1" would be 1-bit black/white.
        self.c = c
        self.s = s
        self.cache_dir = cache_dir
        self.font = ImageFont.truetype(font_path, font_size)
        self.ttfont = TTFont(font_path)
        self.cache = {}
        
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            # Preload everything already cached in that dir
            for filename in os.listdir(cache_dir):
                if filename.endswith(".png") and filename.startswith("U+"):
                    path = os.path.join(cache_dir, filename)
                    img = Image.open(path).convert(self.img_mode)
                    # decode codepoint from filename
                    codepoint = int(filename[2:6], 16)
                    self.cache[chr(codepoint)] = img
            
    def _has_glyph(self, char):
        codepoint = ord(char)
        for table in self.ttfont['cmap'].tables:
            if codepoint in table.cmap:
                return True
        return False

    def _filename(self, char):
        """Generate a filename for the cached glyph."""
        # Use Unicode codepoint as filename (safe across all scripts)
        codepoint = f"U+{ord(char):04X}.png"
        return os.path.join(self.cache_dir, codepoint)


    def _concat(self, images):
        assert len(images)
        total_width = sum(img.width for img in images)
        result = Image.new(self.img_mode, (total_width, images[0].height), 0)

        x_offset = 0
        for img in images:
            result.paste(img, (x_offset, 0))
            x_offset += img.width

        return result

    def _render(self, char):
        """Return glyph image from cache, load/save as needed."""
        if char in self.cache:
            return self.cache[char]

        if self.cache_dir:
            glyph_file = self._filename(char)
            if os.path.exists(glyph_file):
                # Load from disk cache
                img = Image.open(glyph_file).convert(self.img_mode)
                self.cache[char] = img
                return img

        if not self._has_glyph(char):
            print(f"Warning: {char} misses glyph")
            
        # Render if not cached
        # Get bounding box and glyph size
        bbox = self.font.getbbox(char)  # (x0, y0, x1, y1)
        # Fixed canvas height for all glyphs
        ascent, descent = self.font.getmetrics()
        canvas_height = ascent + descent
        canvas_width = bbox[2] - bbox[0]
        # Create image
        img = Image.new(self.img_mode, (canvas_width, canvas_height), 0)
        draw = ImageDraw.Draw(img)
        # Draw with baseline alignment
        fill_value = 1 if self.img_mode == "1" else 255 #white in 1-bit or grayscale or RGB 
        draw.text((-bbox[0], 0), char, fill=fill_value, font=self.font)

        #cache it
        self.cache[char] = img
        #save it
        if self.cache_dir:
            img.save(self._filename(char))

        #width, height = img.size
        #print(f"Char: {char} Width: {width}, Height: {height}")
        print(f"Char: {char} Width: {canvas_width}, Height: {canvas_height}")
        
        return img


    def __call__(self, chars):
        images = []
        ngrams = []
        for i in range(0, len(chars), self.s):
            imgs = [self._render(ch) for ch in chars[i:i+c]]
            ngram = chars[i:i+self.c]
            while len(imgs) < self.c:
                imgs.append(self._render(" "))
                ngram += " "
            images.append(self._concat(imgs))
            ngrams.append(ngram)
        return ngrams, images
    

if __name__ == "__main__":

    import sys
    
    chars = sys.argv[1]
    assert len(chars)

    cache_dir = None #"glyph_cache"
    font_path = "fonts/NotoSansMono-VariableFont_wdth,wght.ttf"
    font_size = 32
    img_mode = "L"
    c = 5  # chunk size [1, Inf)
    s = 4  # step / overlap [1, c] (1: maximum overlap, c: no overlap)
    assert c>0
    assert s>0 and s<=c

    glyph_cache = GlyphCache(font_path, font_size=font_size, img_mode=img_mode, c=c, s=s, cache_dir=cache_dir)
    ngrams, images = glyph_cache(chars)
    for ngram, image in zip(ngrams, images):
        image.show()
        arr = np.array(image)
        print(f"Chars: {ngram} -> {arr.shape} {arr.dtype}")



        
