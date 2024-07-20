import os
from os.path import join, isfile
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from openai import OpenAI
import requests
from matplotlib import pyplot as plt
from io import BytesIO
from itertools import zip_longest
import textwrap
import shutil
import rembg
from resource_lib import ResourceLib

def draw_text(image, annotation, font_path="fonts/BarlowSemiCondensed-Black.ttf", text_color='blush_pink', font_size = 100, write_mode = '', text_box = ()):
    """
    Draws text on an image at a specified location with a specified font, color, and size.

    Parameters:
    image (PIL.Image): The image to draw text on.
    annotation (str): The text to draw.
    font_path (str, optional): The path to the font file. Defaults to "fonts/BarlowSemiCondensed-Black.ttf".
    text_color (str, optional): The color of the text. Defaults to 'blush_pink'.
    font_size (int, optional): The size of the font. Defaults to 100.
    write_mode (str, optional): The mode to write the text. Can be 'top_header' or 'custom_position'. Defaults to ''.
    text_box (tuple, optional): The bounding box for the text. Give as ((x_top_left, y_top_left), (x_bottom_right, y_bottom_right))

    Returns:
    PIL.Image: The image with the text drawn on it.
    """
    if write_mode == 'top_header':
        if __name__ == "__main__":
            print("WARNING: write mode top_header activated, so other parameters are ignored")
        font_size = 150
        # width of one letter is around 60 px per letter (font size 100), so 120 px per letter for font size 200
        letter_width = font_size * 0.52
        max_line_width = 2048 * 0.95 # safety margin
        lines = textwrap.wrap(annotation, width=int(max_line_width / letter_width))
        text_location = (0, 50) # set height of text
    if write_mode == 'specify_text_box':
        # find font size based on text_box size
        text_box_width = text_box[1][0] - text_box[0][0]
        text_box_height = text_box[1][1] - text_box[0][1]
        
        # find font size based on text_box size
        font_size = text_box_width / len(annotation)
        
        max_letters_per_line = text_box_width / font_size
        
        lines = textwrap.wrap(annotation, width=max_letters_per_line)
        
        text_location = text_box[0]
    else:
        raise ValueError("specified write_mode not available")
        
        
            
        
        
        
    text_color_dict = {
                'white': (255, 255, 255),
                'black': (0, 0, 0),
                'classic_blue': (0, 119, 204),
                'living_coral': (255, 111, 97),
                'neo_mint': (143, 220, 191),
                'terracotta': (197, 110, 91),
                'faded_denim': (99, 112, 129),
                'mustard_yellow': (255, 211, 105),
                'blush_pink': (245, 176, 203),
                'olive_green': (110, 113, 77),
                'rich_maroon': (134, 38, 51),
                'dusty_rose': (186, 121, 121),
                'sage_green': (165, 188, 166),
                'powder_blue': (181, 208, 232),
                'charcoal_gray': (85, 85, 85),
                'goldenrod': (217, 191, 119),
                'peachy_keen': (255, 176, 124),
                'charcoal_text': (59, 59, 59)
            }
    draw = ImageDraw.Draw(image)
    font_path = 'fonts/opensans.ttf'
    font = ImageFont.truetype(font_path, font_size)
    font.set_variation_by_name('Bold')
    text_color = text_color_dict.get(text_color, (0, 0, 0))

    

    for line in lines:
        if write_mode == 'top_header':
            annotation_width = font.getlength(line)
            text_location = (int((2048 - annotation_width) / 2), text_location[1])
        draw.text(text_location, line, fill=text_color, font=font)
        height = font.getbbox(line)[3] - font.getbbox(line)[1]
        text_location = (text_location[0], text_location[1] + height)
            

    return image



def paste_image_on_background_to_fit(image, background, target_size = (2048, 2048), relative_size = 1):
    """_summary_

    Args:
        image (_type_): _description_
        background (_type_): _description_
        target_size (tuple, optional): _description_. Defaults to (2048, 2048).
        relative_size (int, optional): How big the pasted image should be in relation to the background; 0.8 means width will become 80% of background width. Defaults to 1. 

    Returns:
        _type_: _description_
    """
    width, height = image.size
    
    upper_left_coord = (int(target_size[0] * (1-relative_size) / 2) , int(target_size[1] * (1-relative_size) / 2))
    target_size = (int(target_size[0] * relative_size), int(target_size[1] * relative_size))
    if (width, height) == target_size:
        background.paste(image, upper_left_coord, image)
        return background
    elif width == height:
        # resize to 2048x2048
        image = image.resize(target_size)
        background.paste(image, upper_left_coord, image)
        return background
    elif width > height:
        ratio = target_size[0] / width
        new_width = target_size[0] 
        new_height = int(height * ratio)
        image = image.resize((new_width, new_height))
        background.paste(image, upper_left_coord, image)
        return background
    elif width < height:
        ratio = target_size[1] / height
        new_width = int(width * ratio)
        new_height = target_size[1]
        image = image.resize((new_width, new_height))
        background.paste(image, upper_left_coord, image)
        return background
        
        
    
    
def create_image_from_template(template_type:str,input_image:str, output_path:str, annotation = "", icon_keyword = ""):
    # check if we are in correct dir
    if not str(os.getcwd()).endswith('PersonalUseWebcrawlers'):
        # get wanted dir by removing the character after PersonalUseWebcrawlers
        wanted_dir = str(os.getcwd()).split('PersonalUseWebcrawlers')[0] + 'PersonalUseWebcrawlers'
        os.chdir(wanted_dir)
    
    if annotation == "...":
        annotation = ""
    if template_type.lower() == 'hoofdfoto':
        return input_image
    if template_type.lower() == 'lifestyle':
        # use stock photo
        return input_image
    elif template_type.lower() == 'infographic meerdere usp':
        target_size = (2048, 2048)
        
        if not isinstance(annotation, list):
            raise ValueError("Annotation should be a list of 4 strings for template type 'infographic meerdere usp'")
        if not len(annotation) == 4:
            raise ValueError("Annotation should be a list of 4 for template type 'infographic meerdere usp'")

        if not isinstance(icon_keyword, list):
            raise ValueError("Icon keyword should be a list of 4 strings for template type 'infographic meerdere usp'")
        if not len(icon_keyword) == 4:
            raise ValueError("Icon keyword should be a list of 4 for template type 'infographic meerdere usp'")
        
        # create white image
        img = Image.new("RGB", target_size, "white")
        
        background = Image.open(input_image)
        background = background.resize(target_size)
        if background.mode != 'RGBA':
            background = background.convert('RGBA')
        img.paste(background, (0, 0), background)
        
        # add white bar at the right of the image for the text to be written on, with top left, top right, bottom right, bottom left coordinates being (1400,0), (2048,0), (2048,2048), (1400,2048)
        white_bar = Image.new("RGB", (target_size[0] - 1400, target_size[1]), "white")
        img.paste(white_bar, (1400, 0))
        
        icon_positions = [(1630, 100), (1630, 100 + 532), (1630, 100 + 2*532), (1630, 100 + 3*532)]
        
        
        
        # get all icons from nounproject
        for current_icon_keyword, icon_position in zip(icon_keyword, icon_positions): 
            icon = ResourceLib().get_icon_from_keyword(keyword=current_icon_keyword, color='black', size=150) # is custom IconResource object
            icon_path = icon.get_image_path()
            icon_image = Image.open(icon_path)
            # resize to 150x150, and paste to img at positions given by icon_positions, and paste onto img
            icon_image = icon_image.resize((150, 150))
            # print size of icon_image
            print(icon_image.size)
            img.paste(icon_image, icon_position, icon_image)
        
        text_positions = [(1630, 100 + 150), (1630, 100 + 532 + 150), (1630, 100 + 2*532 + 150), (1630, 100 + 3*532 + 150)]
        
        for current_annotation, text_position_top_left in zip(annotation, text_positions):
            
            img = draw_text(img, current_annotation, font_path='fonts/opensans.ttf',text_color='charcoal_text', font_size=100, write_mode='specify_text_box', text_box = ((text_position_top_left[0], text_position_top_left[1]), (text_position_top_left[0] + 500, text_position_top_left[1] + 300)))

        
        img.show()
        
    else:
        # backup: Just use background and add simple text
        target_size = (2048, 2048)
        # create white image 
        img = Image.new("RGB", target_size, "white")
        
        background = Image.open("pre_photos/backgrounds/5.jpg")
        background = background.resize(target_size)
        if background.mode != 'RGBA':
            background = background.convert('RGBA')
        img.paste(background, (0, 0), background)
        
        
        product_image = Image.open(input_image)
        product_image = rembg.remove(product_image)
        
        if product_image.mode != 'RGBA':
            product_image = product_image.convert('RGBA')
        img = paste_image_on_background_to_fit(product_image, img, relative_size=0.7)
        
        img = draw_text(img, annotation, font_path='fonts/opensans.ttf',text_color='charcoal_text', font_size=100, write_mode='top_header')
        
        files_in_output_path = [f for f in os.listdir(output_path) if isfile(join(output_path, f))]
        for i in range(10):
            if f'image{i}.jpg' not in files_in_output_path:
                img.save(f'{output_path}/image{i}.jpg')
                break
            
            
            
            
            
def add_trash_can_to_image(trashcan_image):
    background_img = Image.open(os.path.join('..', 'pre_photos', 'extra','trashcan_background.jpg'))
    trashcan_image = Image.open(trashcan_image)
    
    # resize trashcan_image to max width of 850px 
    width, height = trashcan_image.getbbox()[2] - trashcan_image.getbbox()[0], trashcan_image.getbbox()[3] - trashcan_image.getbbox()[1]
    max_width = 620
    ratio = max_width / width
    new_width = max_width
    new_height = int(height * ratio)
    trashcan_image = trashcan_image.resize((new_width, new_height))
    
    #TODO: remove backgrounds with API
    
    # remove white background from trashcan_image
    image = trashcan_image
    image = image.convert("RGBA")
    image_data = image.getdata()
    print(image_data)
    new_data = []
    for item in image_data:
        item0 = item[0]
        if item[0] in list(range(240, 256)):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    image.putdata(new_data)
    trashcan_image = image

    # lower left corner of trashcan_image should be at (0, 1600)
    trashcan_height = trashcan_image.getbbox()[3] - trashcan_image.getbbox()[1]
    background_img.paste(trashcan_image, (100, 1700-trashcan_height), trashcan_image)
    
    trashcan_image_path = os.path.join('temp/trashcan_image.png')
    background_img.save(trashcan_image_path)
    return trashcan_image_path
if __name__ == "__main__":
    # main()
    # create_image_from_template(template_type="Infographic met meerdere USP's", input_image='pre_photos/current_bol_images/image0.jpg', output_path='post_photos', annotation='Vervangbare mesjes')
    # add_trash_can_to_image(os.path.join('temp/trashcan_image_bol.jpg'))
    create_image_from_template(template_type="infographic meerdere usp", input_image='pre_photos/current_bol_images/image0.jpg', output_path='post_photos', annotation=['Vervangbare mesjes', 'Lief voor de kinders', 'Makkelijk te reinigen', 'Lekker slapen'], icon_keyword=['trashcan', 'heart', 'cleaning', 'eyelid'])