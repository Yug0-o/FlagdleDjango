import os
from PIL import Image

def convert_png_to_webp(img_path:str):
    """
    Convert a PNG image to a WEBP image.
    """
    image = Image.open(img_path)
    output_path = img_path.rsplit('.', 1)[0] + '.webp'
    image.save(output_path, 'WEBP')
    os.remove(img_path)


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
    root_folder = "D:/VisualCode_Python/FlagdleDjango/Flagdle/assets"
    convert_folders_png_to_webp(root_folder)