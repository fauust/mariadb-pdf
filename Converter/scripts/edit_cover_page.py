from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import date
import os
import sys

def get_date():
    today = date.today()
    string = today.strftime("%Y-%m")
    return string

def get_platform():

    return "".join(c for c in sys.platform if not c.isdigit()).lower()

def edit_image(im, text, font_type="arial.ttf", fontsize=75):
    font = ImageFont.truetype(font_type, fontsize)

    txt = Image.new('L', (320, fontsize))

    d = ImageDraw.Draw(txt)

    d.text((0, 0), text,  font = font, fill = 255)

    txt=txt.rotate(-45,  expand=1) 

    im.paste( ImageOps.colorize(txt, (0,0,0), (255,255,255)), (900, 0),  txt)
    return im


def edit_cover_page(config):
    image = Image.open("Cover.jpg")
    if config["edit_cover_image"]:
        image = edit_image(image, get_date())
    image.save(os.path.join("temp", "Cover.jpg"))