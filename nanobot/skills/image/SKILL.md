---
name: image
description: Process and analyze images including format conversion, resizing, OCR text extraction, metadata inspection, and visual analysis via multimodal LLM APIs. Use for image manipulation, extraction, and understanding.
metadata: {"nanobot":{"emoji":"🖼️","requires":{"bins":["python3"]}}}
---

# Image Skill

Use Python PIL/Pillow, ImageMagick (if available), and multimodal LLM APIs for image processing.

## Quick Reference

| Task | Command |
|------|---------|
| Convert format | `python3 -c "from PIL import Image; Image.open('a.png').save('a.jpg')"` |
| Resize image | `python3 -c "from PIL import Image; img = Image.open('a.jpg'); img.resize((800,600)).save('a_small.jpg')"` |
| Get info | `python3 -c "from PIL import Image; print(Image.open('a.jpg').size, Image.open('a.jpg').format)"` |
| OCR (tesseract) | `tesseract image.png stdout` |
| Extract EXIF | `python3 -c "from PIL import Image; from PIL.ExifTags import TAGS; print({TAGS.get(k):v for k,v in Image.open('img.jpg')._getexif().items()})"` |

## Basic Operations (Pillow)

```bash
# Convert format
python3 -c "from PIL import Image; Image.open('input.png').save('output.jpg', quality=95)"

# Resize (maintain aspect ratio)
python3 << 'EOF'
from PIL import Image
img = Image.open('input.jpg')
w, h = img.size
new_w = 800
new_h = int(h * new_w / w)
img.resize((new_w, new_h), Image.Resampling.LANCZOS).save('output.jpg')
EOF

# Crop image
python3 -c "from PIL import Image; img = Image.open('a.jpg'); img.crop((100,100,400,400)).save('cropped.jpg')"

# Rotate
python3 -c "from PIL import Image; Image.open('a.jpg').rotate(90, expand=True).save('rotated.jpg')"

# Create thumbnail
python3 << 'EOF'
from PIL import Image
img = Image.open('a.jpg')
img.thumbnail((128, 128))
img.save('thumb.jpg')
EOF
```

## Image Information

```bash
# Basic info
python3 << 'EOF'
from PIL import Image
with Image.open('image.jpg') as img:
    print(f"Format: {img.format}")
    print(f"Mode: {img.mode}")
    print(f"Size: {img.size}")
    print(f"Width: {img.width}, Height: {img.height}")
EOF

# File size
ls -lh image.jpg
python3 -c "import os; print(f'{os.path.getsize(\"image.jpg\") / 1024:.2f} KB')"
```

## OCR Text Extraction

```bash
# Using tesseract (if installed)
tesseract image.png stdout
tesseract image.png output -l eng+chi_sim  # English + Chinese

# Using pytesseract via Python
python3 << 'EOF'
from PIL import Image
import pytesseract
text = pytesseract.image_to_string(Image.open('image.png'), lang='eng')
print(text)
EOF
```

## EXIF Metadata

```bash
# Extract all EXIF data
python3 << 'EOF'
from PIL import Image
from PIL.ExifTags import TAGS

img = Image.open('photo.jpg')
exif = img._getexif()
if exif:
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        print(f"{tag:25s}: {value}")
else:
    print("No EXIF data")
EOF

# Get specific fields
python3 << 'EOF'
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

img = Image.open('photo.jpg')
exif = img._getexif()
if exif:
    make = exif.get(0x010F)  # Camera make
    model = exif.get(0x0110)  # Camera model
    date = exif.get(0x9003)   # Date taken
    print(f"Camera: {make} {model}")
    print(f"Date: {date}")
EOF
```

## Batch Processing

```bash
# Convert all PNG to JPG
for f in *.png; do python3 -c "from PIL import Image; Image.open('$f').save('${f%.png}.jpg')"; done

# Resize all images in directory
for f in *.jpg; do
  python3 << EOF
from PIL import Image
img = Image.open('$f')
w, h = img.size
if w > 1920:
    new_h = int(h * 1920 / w)
    img.resize((1920, new_h), Image.Resampling.LANCZOS).save('resized_$f')
else:
    img.save('resized_$f')
EOF
done
```

## Multimodal LLM Analysis

When you need to understand image content, use multimodal LLM APIs:

```bash
# Encode image to base64 for API calls
python3 << 'EOF'
import base64
with open('image.jpg', 'rb') as f:
    encoded = base64.b64encode(f.read()).decode('utf-8')
    print(f"data:image/jpeg;base64,{encoded}")
EOF
```

Then send to multimodal API (GPT-4V, Gemini, etc.):

```bash
# Example with OpenAI GPT-4V
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4-vision-preview",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "Describe this image"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,'"$(base64 -w0 image.jpg)"'"}}
      ]
    }]
  }'
```

## ImageMagick Commands (if available)

```bash
# Convert format
convert input.png output.jpg

# Resize
convert input.jpg -resize 800x600 output.jpg
convert input.jpg -resize 50% output.jpg

# Crop
convert input.jpg -crop 400x400+100+100 output.jpg

# Quality compression
convert input.jpg -quality 80 output.jpg

# Get info
identify -verbose image.jpg
identify -format "%w %h %f\n" *.jpg
```

## Common Patterns

### Create placeholder image
```bash
python3 -c "from PIL import Image; Image.new('RGB', (800, 600), color='lightgray').save('placeholder.jpg')"
```

### Add watermark (basic)
```bash
python3 << 'EOF'
from PIL import Image, ImageDraw, ImageFont

base = Image.open('photo.jpg').convert('RGBA')
txt = Image.new('RGBA', base.size, (255,255,255,0))
d = ImageDraw.Draw(txt)
d.text((10, 10), "Watermark", fill=(255,255,255,128))
Image.alpha_composite(base, txt).convert('RGB').save('watermarked.jpg')
EOF
```

### Compare two images
```bash
python3 << 'EOF'
from PIL import Image
import math

img1 = Image.open('image1.jpg')
img2 = Image.open('image2.jpg')

if img1.size != img2.size:
    print(f"Different sizes: {img1.size} vs {img2.size}")
else:
    diff = 0
    pixels1 = img1.load()
    pixels2 = img2.load()
    for i in range(img1.width):
        for j in range(img1.height):
            p1 = pixels1[i, j]
            p2 = pixels2[i, j]
            diff += sum(abs(a-b) for a, b in zip(p1, p2))
    print(f"Total difference: {diff}")
EOF
```

## Tips

- Pillow is usually pre-installed; install with `pip install Pillow` if needed
- For OCR: `apt install tesseract-ocr` (Linux) or `brew install tesseract` (macOS)
- For ImageMagick: `apt install imagemagick` or `brew install imagemagick`
- Always handle exceptions in production scripts
- Use `Image.Resampling.LANCZOS` for high-quality resizing
- Save original before destructive operations
