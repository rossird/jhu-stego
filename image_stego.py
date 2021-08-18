# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 18:07:57 2021

@author: richa
"""

import numpy
from pathlib import Path
from PIL import Image
    
def encode_image(message: str, image_path: Path) -> Path:
    """
    Encode a string message in an image file. Image should be a .png.
    """
    new_path   = new_image_path(image_path)
    
    image      = Image.open(image_path, 'r')
    new_pixels = encode(message, image)
    new_image  = Image.fromarray(numpy.uint8(new_pixels), 'RGB')
    
    new_image.save(new_path)
    return new_path

def decode_image(image_path: Path) -> str:
    image = Image.open(image_path, 'r')
    
    pixels = numpy.array(image)
    (h,w,_) = pixels.shape        
    pixels = numpy.resize(pixels, (h*w,3))
    
    num_pixels = len(pixels)
    num_chars  = num_pixels * 3
    
    message = ['\0'] * num_chars
        
    pixel_ix = 0
    char_ix  = 0
    
    # Store one byte in three pixels
    # Each pixel has 3 values, so there are 9 values in 3 pixels
    # We will store 1 bit in the first 8 of the 9 values
    while pixel_ix + 2 < num_pixels:
        
        b = 0
        
        b |= (pixels[pixel_ix][0]  & 1)   << 7
        b |= (pixels[pixel_ix][1]  & 1)   << 6
        b |= (pixels[pixel_ix][2]  & 1)   << 5
        b |= (pixels[pixel_ix+1][0]  & 1) << 4
        b |= (pixels[pixel_ix+1][1]  & 1) << 3
        b |= (pixels[pixel_ix+1][2]  & 1) << 2
        b |= (pixels[pixel_ix+2][0]  & 1) << 1
        b |= (pixels[pixel_ix+2][1]  & 1) << 0
        
        message[char_ix] = chr(b)
        
        pixel_ix += 3
        char_ix += 1
        
    return ''.join(message).strip('\x00')
    
def new_image_path(image_path: Path) -> Path:
    new_name = image_path.stem + '_stego' + image_path.suffix
    new_path = Path(image_path.parent / new_name)
    return new_path

def encode(message: str, image: Image) -> numpy.array:
    
    pixels = numpy.array(image)
    (h,w,_) = pixels.shape        
    pixels = numpy.resize(pixels, (h*w,3))
    
    num_pixels = len(pixels)
    num_chars  = len(message)
    
    if num_chars > num_pixels * 3:
        print("Not enough room to store %d characters! Message will be truncated".format(num_chars))
        
    pixel_ix = 0
    char_ix  = 0
    
    # Store one byte in three pixels
    # Each pixel has 3 values, so there are 9 values in 3 pixels
    # We will store 1 bit in the first 8 of the 9 values
    while(pixel_ix + 2 < num_pixels and char_ix < num_chars):
        
        d = "{:08b}".format(ord(message[char_ix]))
        
        r   = set_lsb(pixels[pixel_ix][0],  d[0])
        g   = set_lsb(pixels[pixel_ix][1],  d[1])
        b   = set_lsb(pixels[pixel_ix][2],  d[2])
        pixels[pixel_ix] = (r,g,b)
        
        r = set_lsb(pixels[pixel_ix+1][0],  d[3])
        g = set_lsb(pixels[pixel_ix+1][1],  d[4])
        b = set_lsb(pixels[pixel_ix+1][2],  d[5])
        pixels[pixel_ix+1] = (r,g,b)
        
        r = set_lsb(pixels[pixel_ix+2][0],  d[6])
        g = set_lsb(pixels[pixel_ix+2][1],  d[7])
        b = pixels[pixel_ix+2][2]
        pixels[pixel_ix+2] = (r,g,b)
        
        pixel_ix += 3
        char_ix += 1
        
    # Fill the rest of the pixels with 0
    while(pixel_ix < num_pixels):
        r = set_lsb(pixels[pixel_ix][0], 0)
        g = set_lsb(pixels[pixel_ix][1], 0)
        b = set_lsb(pixels[pixel_ix][2], 0)
        pixels[pixel_ix] = (r,g,b)
        
        pixel_ix += 1
        
    return numpy.resize(pixels, (h,w,3))

def set_lsb(value, bit):
    value = (value & ~1) | int(bit)
    return value
    
        
encoded_path = encode_image("BUYGMENOW", Path("Jaguar_Smaller.png"))
print(decode_image(encoded_path))