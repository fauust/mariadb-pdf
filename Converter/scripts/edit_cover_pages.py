import os
from PIL import Image


def edit_covers():
    files = os.listdir("cover_images")
    if "transform_to_png.py" in files:
        files.remove("transform_to_png.py")
    for filename in files:
        filepath = os.path.join("cover_images", filename)
        filend = filepath[-3:]
        if filend == "jpg":
            convert(filepath)
    


def convert(filename):
      file =  Image.open(filename)
      file.resize((1144, 1600))

      namefile = filename[:-3]+"png"
      file.save(namefile)
