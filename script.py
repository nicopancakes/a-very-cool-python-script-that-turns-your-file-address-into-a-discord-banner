import os
import requests
from PIL import Image, ImageSequence
from io import BytesIO
import re

def get_tenor_direct_url(page_url):
    """Extracts the direct Tenor GIF/MP4 URL from a Tenor webpage."""
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(page_url, headers=headers)
    html = r.text

    match = re.search(r'<meta itemprop="contentUrl" content="(.*?)"', html)
    if match:
        return match.group(1)
    return None


def download_or_open(source):
    """Load image/GIF from URL/local file, including Tenor support."""

    if "tenor.com" in source:
        direct = get_tenor_direct_url(source)
        if not direct:
            print("Could not extract GIF URL from Tenor.")
            return None
        source = direct
        print(f"Tenor GIF URL found:\n{source}")

    try:
        if source.startswith(("http://", "https://")):
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(source, headers=headers)
            r.raise_for_status()
            return Image.open(BytesIO(r.content))
        else:
            return Image.open(source)

    except Exception as e:
        print(f"Error loading image: {e}")
        return None


def resize_image(img, size=(600, 240)):
    return img.resize(size, Image.LANCZOS)


def save_to_downloads(img, filename):
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    os.makedirs(downloads, exist_ok=True)
    path = os.path.join(downloads, filename)
    img.save(path)
    print(f"Saved to: {path}")


def convert(source):
    img = download_or_open(source)
    if img is None:
        return

    if getattr(img, "is_animated", False):
        frames = []
        for frame in ImageSequence.Iterator(img):
            f = frame.convert("RGBA")
            f = resize_image(f)
            frames.append(f)

        output = os.path.join(os.path.expanduser("~"), "Downloads", "converted.gif")
        frames[0].save(output, save_all=True, append_images=frames[1:], loop=0)
        print(f"Saved animated GIF to: {output}")

    else:
        img = resize_image(img.convert("RGBA"))
        output = os.path.join(os.path.expanduser("~"), "Downloads", "converted.png")
        img.save(output)
        print(f"Saved image to: {output}")

src = input("Enter image/GIF path or URL: ")
convert(src)
