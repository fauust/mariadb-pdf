from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import date
import os

def get_date():
    today = date.today()
    string = today.strftime("%Y-%m")
    return string


def edit_image(image, text, font_type="arial", fontsize=75):

    im=Image.open(image)

    font = ImageFont.truetype(font_type, fontsize)

    txt = Image.new('L', (320, fontsize))

    d = ImageDraw.Draw(txt)

    d.text((0, 0), text,  font = font, fill = 236)

    txt=txt.rotate(-45,  expand=1)

    im.paste( ImageOps.colorize(txt, (0,0,0), (255,255,255)), (900, 0),  txt)
    return im


def edit_cover_page():
    image = edit_image("Cover.jpg", get_date())
    image.save(os.path.join("temp", "Cover.jpg"))