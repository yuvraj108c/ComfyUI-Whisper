from PIL import ImageDraw, ImageFont, Image
from .utils import tensor2pil, pil2tensor, tensor2Mask
import math
import os

FONT_DIR = os.path.join(os.path.dirname(__file__),"fonts")

class AddSubtitlesToFramesNode:
    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": { 
                "images": ("IMAGE",),
                "alignment" : ("whisper_alignment",),
                "font_color": ("STRING",{
                    "default": "white"
                }),
                "font_family": (os.listdir(FONT_DIR),),
                "font_size": ("INT",{
                    "default": 50,
                    "step":5,
                    "display": "number"
                }),
                "x_position": ("INT",{
                    "default": 500,
                    "step":50,
                    "display": "number"
                }),
                "y_position": ("INT",{
                    "default": 500,
                    "step":50,
                    "display": "number"
                }),
                "video_fps": ("INT",{
                    "default": 24,
                    "step":1,
                    "display": "number"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK",)
    RETURN_NAMES = ("IMAGE","MASK",)
    FUNCTION = "add_subtitles_to_frames"
    CATEGORY = "whisper"


    def add_subtitles_to_frames(self, images, alignment, font_family, font_size, font_color, x_position, y_position, video_fps):
        pil_images = tensor2pil(images)

        pil_images_with_text = []
        pil_images_masks = []

        font = ImageFont.truetype(os.path.join(FONT_DIR,font_family), font_size)

        if len(alignment) == 0:
            pil_images_with_text = pil_images

            # create mask
            width, height = pil_images[0].size
            black_img = Image.new('RGB', (width, height), 'black')
            pil_images_masks.extend([black_img]*len(pil_images))
        

        last_frame_no = 0
        for i in range(len(alignment)):
            alignment_obj = alignment[i]
            start_frame_no = math.floor(alignment_obj["start"] * video_fps)
            end_frame_no = math.floor(alignment_obj["end"] * video_fps)

            # create images without text
            for i in range(last_frame_no, start_frame_no):
                img = pil_images[i].convert("RGB")
                width, height = img.size
                pil_images_with_text.append(img)

                # create mask
                black_img = Image.new('RGB', (width, height), 'black')
                pil_images_masks.append(black_img)  


            for i in range(start_frame_no,end_frame_no):
                img = pil_images[i].convert("RGB")
                width, height = img.size

                # add text to video frames
                d = ImageDraw.Draw(img)
                d.text((x_position, y_position), alignment_obj["value"], fill=font_color,font=font)
                pil_images_with_text.append(img)

                # create mask
                black_img = Image.new('RGB', (width, height), 'black')
                d = ImageDraw.Draw(black_img)
                d.text((x_position, y_position), alignment_obj["value"], fill="white",font=font)    
                pil_images_masks.append(black_img)    
            
            last_frame_no = end_frame_no


        tensor_images = pil2tensor(pil_images_with_text)
        tensor_masks = tensor2Mask(pil2tensor(pil_images_masks))

        return (tensor_images,tensor_masks,)
