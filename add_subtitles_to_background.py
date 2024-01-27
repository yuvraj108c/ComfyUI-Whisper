from PIL import ImageDraw, ImageFont, Image
from .utils import pil2tensor,tensor2pil
import math
import os
import random

FONT_DIR = os.path.join(os.path.dirname(__file__),"fonts")

class AddSubtitlesToBackgroundNode:
    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": { 
                "images": ("IMAGE",),
                "alignment" : ("whisper_alignment",),
                "font_family": (os.listdir(FONT_DIR),),
                "video_fps": ("INT",{
                    "default": 24,
                    "step":1,
                    "display": "number"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGE",)
    FUNCTION = "add_subtitles_to_background"
    CATEGORY = "whisper"


    def add_subtitles_to_background(self, images, alignment, font_family, video_fps):
        pil_images = tensor2pil(images)

        width, height = pil_images[0].size
        bg_image = Image.new("RGB", (width, height), (255, 255, 255))

        font_sizes = [40, 50, 60, 85, 100] 

        final_pil_images = []

        if len(alignment) == 0:
            bg_image = Image.new("RGB", (width, height), (255, 255, 255))
            final_pil_images.extend([bg_image]*len(pil_images))
        
        last_frame_no = 0
        for i in range(len(alignment)):
            alignment_obj = alignment[i]
            start_frame_no = math.floor(alignment_obj["start"] * video_fps)
            end_frame_no = math.floor(alignment_obj["end"] * video_fps)

            word = alignment_obj["value"]

            # create images with no texts
            for i in range(last_frame_no, start_frame_no):
                bg_image = Image.new("RGB", (width, height), (255, 255, 255))
                final_pil_images.append(bg_image)
                print('blank')
            

            for i in range(start_frame_no,end_frame_no):
                used_positions = []

                draw = ImageDraw.Draw(bg_image)

                # Loop to add text at random positions and sizes without overlapping
                for _ in range(50):
                    # Random position
                    x = random.randint(0, width - 100)
                    y = random.randint(0, height - 30)
                    
                    # Random font size
                    font_size = random.choice(font_sizes)
                    font = ImageFont.truetype(os.path.join(FONT_DIR,font_family), font_size)
                    

                    # Calculate the text bounding box using draw.textbbox()
                    text_bbox = draw.textbbox((x, y), word, font=font)
                    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
                    
                    text_box = (x, y, x + text_width, y + text_height)
                    
                    # Check if the current word's bounding box overlaps with any previously used positions
                    overlap = any(
                        (
                            x1 < text_box[2] and x2 > text_box[0] and
                            y1 < text_box[3] and y2 > text_box[1]
                        )
                        for x1, y1, x2, y2 in used_positions
                    )
                    
                    # If there's no overlap, add the word to the image and update the used positions list
                    if not overlap:
                        used_positions.append(text_box)
                        draw.text((x, y), word, fill=(0, 0, 0), font=font)

                final_pil_images.append(bg_image)
                bg_image = Image.new("RGB", (width, height), (255, 255, 255))
            
            last_frame_no = end_frame_no

   
        tensor_images = pil2tensor(final_pil_images)

        return (tensor_images,)
