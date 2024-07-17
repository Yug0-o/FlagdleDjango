from fileinput import filename
import os
from PIL import Image

import sys
sys.path.append('D:\\VisualCode_Python\\FlagdleDjango\\Flagdle\\game')
import Base64EncoderDecoder as utf8_To_b64

def convert_png_to_webp(img_path:str,BASE10decoding=0, BASE10encoding=0):
    """
    Convert a PNG image to a WEBP image.
    """
    if not os.path.isfile(img_path):
        raise FileNotFoundError(f'File {img_path} does not exist.')

    # sanitize path
    img_path = os.path.abspath(img_path)
    
    image = Image.open(img_path)

    output_path = img_path.rsplit('.', 1)[0] + '.webp'
    
    image.save(output_path, 'WEBP')

    
    path, filename = os.path.split(img_path)
    if filename != 'icon.png':
        if BASE10encoding:
            filename = filename.rsplit('.', 1)[0]
            base64_filename = utf8_To_b64.utf8_to_base64(filename)
            base64_path = os.path.join(path, base64_filename + '.webp')
            if os.path.isfile(base64_path):
                os.remove(base64_path)
                
            os.rename(output_path, base64_path)

    try:
        os.remove(img_path)
    except:
        pass
    
    


def convert_folders_png_to_webp(input_path:str):
    """
    Convert all PNG images in a folder and its subfolders to WEBP images.
    """
    if not os.path.isdir(input_path):
        raise FileNotFoundError(f'Folder {input_path} does not exist.')
    for root, _, files in os.walk(input_path):
        for filename in files:
            if filename.lower().endswith('.png'):
                file_path = os.path.join(root, filename)
                convert_png_to_webp(file_path)
                print(f'Converted and deleted {file_path.split(input_path)[1][1:]} to WEBP.')


if __name__ == '__main__':
    root_folder = "D:/VisualCode_Python/FlagdleDjango/Flagdle/assets/country/country_icon.png"
    convert_png_to_webp(root_folder)