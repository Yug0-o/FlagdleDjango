from fileinput import filename
import os
from PIL import Image

import sys
sys.path.append('D:\\VisualCode_Python\\FlagdleDjango\\Flagdle\\game')
from Base32EncoderDecoder import utf8_to_base32, base32_to_utf8

def convert_png_to_webp(img_path:str,BASE32decoding=0, BASE32encoding=0):
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
    if "icon" not in filename:
        if BASE32encoding:
            filename = filename.rsplit('.', 1)[0]
            base32_filename = utf8_to_base32(filename)
            base32_path = os.path.join(path, base32_filename + '.webp')
            if os.path.isfile(base32_path):
                os.remove(base32_path)
                
            os.rename(output_path, base32_path)

    try:
        os.remove(img_path)
        if BASE32decoding and not BASE32encoding:
            filename = filename.rsplit('.', 1)[0]
            base32_filename = utf8_to_base32(filename)
            base32_path = os.path.join(path, base32_filename + '.webp')
            if os.path.isfile(base32_path):
                os.remove(base32_path)
    except:
        pass
    
    


def convert_folders_png_to_webp(input_path:str, BASE32decoding=0, BASE32encoding=0):
    """
    Convert all PNG images in a folder to WEBP images.
    """
    if not os.path.isdir(input_path):
        raise FileNotFoundError(f'Folder {input_path} does not exist.')
    for root, _, files in os.walk(input_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            convert_png_to_webp(file_path, BASE32decoding, BASE32encoding)
            print(f'Converted and deleted {file_path.split(input_path)[1][1:]} to WEBP.')


if __name__ == '__main__':
    root_folder = "D:/VisualCode_Python/FlagdleDjango/Flagdle/assets/flags/World"
    BASE32decoding, BASE32encoding = 1, 0
    print(f"Converting all PNG images in {root_folder} to WEBP.")
    convert_folders_png_to_webp(root_folder, BASE32decoding, BASE32encoding)