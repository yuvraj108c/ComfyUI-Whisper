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
                "num_words": ("INT",{
                    "default": 25,
                    "step":1,
                    "display": "number"
                }),
                "text_displacement": ("INT",{
                    "default": 10,
                    "step":1,
                    "display": "number"
                }),
                "font_size_displacement": ("INT",{
                    "default": 3,
                    "step":1,
                    "display": "number"
                }),
                "min_font_size": ("INT",{
                    "default": 15,
                    "step":1,
                    "display": "number"
                }),
                "max_font_size": ("INT",{
                    "default": 75,
                    "step":1,
                    "display": "number"
                }),
                "video_fps": ("FLOAT",{
                    "default": 24.0,
                    "step":1,
                    "display": "number"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGE",)
    FUNCTION = "add_subtitles_to_background"
    CATEGORY = "whisper"


    def add_subtitles_to_background(self, images, alignment, font_family, text_displacement, font_size_displacement,num_words, min_font_size, max_font_size, video_fps):
        pil_images = tensor2pil(images)

        frame_width, frame_height = pil_images[0].size
        bg_image = Image.new("RGB", (frame_width, frame_height), (255, 255, 255))

        background_color = (0, 0, 0)
        text_color = (255,255,255)

        # Randomly scatter the initial (x, y) positions and font sizes within the image size
        positions = [(random.randint(0, frame_width - 100), random.randint(0, frame_height - 30)) for _ in range(num_words)]
        # create N font sizes in defined range
        font_sizes = [random.randint(min_font_size, max_font_size) for _ in range(100)]

        final_pil_images = []

        if len(alignment) == 0:
            bg_image = Image.new("RGB", (frame_width, frame_height), background_color)
            final_pil_images.extend([bg_image]*len(pil_images))
        
        last_frame_no = 0
        for x in range(len(alignment)):
            alignment_obj = alignment[x]
            start_frame_no = math.floor(alignment_obj["start"] * video_fps)
            end_frame_no = math.floor(alignment_obj["end"] * video_fps)

            word = alignment_obj["value"]

            # create images with no texts
            for _ in range(last_frame_no, start_frame_no):
                bg_image = Image.new("RGB", (frame_width, frame_height), background_color)
                final_pil_images.append(bg_image)
            

            for _ in range(start_frame_no,end_frame_no):
            
                # Create a blank frame with background color
                bg_image = Image.new("RGB", (frame_width, frame_height), background_color)
                draw = ImageDraw.Draw(bg_image)

                # Create new lists to store the updated positions and font sizes
                updated_positions = []
                updated_font_sizes = []

                # Loop to add text at (x, y) positions and sizes without overlapping
                for i, pos in enumerate(positions):
                    x, y = pos  # Unpack the (x, y) position from the tuple
                    
                    # Randomly choose a direction (up, down, left, or right) and apply displacement
                    direction = random.choice(["up", "down", "left", "right"])
                    if direction == "up":
                        y -= text_displacement
                    elif direction == "down":
                        y += text_displacement
                    elif direction == "left":
                        x -= text_displacement
                    elif direction == "right":
                        x += text_displacement

                    # Ensure that the new (x, y) positions stay within the image boundaries
                    x = max(0, min(x, frame_width - 100))
                    y = max(0, min(y, frame_height - 30))

                    # Randomly add/subtract X pixels from the font size
                    font_size = font_sizes[i] + random.choice([-font_size_displacement, font_size_displacement])
                    font_size = int(max(min_font_size, min(font_size, max_font_size)))  # Ensure font size is within the desired range

                    # Calculate the text bounding box
                    font = ImageFont.truetype(os.path.join(FONT_DIR,font_family), size=font_size)
                    text_bbox = draw.textbbox((x, y), word, font=font)

                    # Collision detection: Check if the current text box intersects with any previously added text boxes
                    overlap = any(
                        (
                            x1 < text_bbox[2] and x2 > text_bbox[0] and
                            y1 < text_bbox[3] and y2 > text_bbox[1]
                        )
                        for x1, y1, x2, y2 in updated_positions
                    )

                    # Use a while loop to keep trying to place the word until no overlap is detected
                    while overlap:
                        # Randomly adjust the position and font size
                        x, y = random.randint(0, frame_width - 100), random.randint(0, frame_height - 30)
                        font_size = int(random.randint(min_font_size, max_font_size))

                        # Recalculate the text bounding box
                        font = ImageFont.truetype(os.path.join(FONT_DIR,font_family), size=font_size)
                        text_bbox = draw.textbbox((x, y), word, font=font)

                        # Check for overlap again
                        overlap = any(
                            (
                                x1 < text_bbox[2] and x2 > text_bbox[0] and
                                y1 < text_bbox[3] and y2 > text_bbox[1]
                            )
                            for x1, y1, x2, y2 in updated_positions
                        )

                    # Add the word to the frame and update the used positions and font sizes lists
                    draw.text((x, y), word, fill=text_color, font=font)
                    updated_positions.append((x, y, text_bbox[2], text_bbox[3]))
                    updated_font_sizes.append(font_size)

                # Update the positions and font sizes lists with the new positions and font sizes
                positions = [(x1, y1) for x1, y1, _, _ in updated_positions]
                font_sizes = updated_font_sizes

                final_pil_images.append(bg_image)
                bg_image = Image.new("RGB", (frame_width, frame_height), text_color)
            
            last_frame_no = end_frame_no

        # create missing black images at the end
        missing_frames_count = len(pil_images) - len(final_pil_images)
        for _ in range(missing_frames_count):
            bg_image = Image.new("RGB", (frame_width, frame_height), background_color)
            final_pil_images.append(bg_image)

        tensor_images = pil2tensor(final_pil_images)

        return (tensor_images,)
