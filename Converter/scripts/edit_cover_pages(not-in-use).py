""" NOT IN USE"""


import os
from PIL import Image


def edit_covers():
    files = os.listdir("cover_images")
    for filename in files:
        filepath = os.path.join("cover_images", filename)
        filend = filepath[-3:]
        if filend == "jpg":
            convert(filepath)
    

def convert(filename):
      file = Image.open(filename)
      file = file.resize((int(1144 / 1.5), int(1600 / 1.5)))

      namefile = filename[:-3]+"png"
      file.save(namefile)
