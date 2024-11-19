from PIL import ImageDraw, ImageFont, Image
from .utils import tensor2pil, pil2tensor, tensor2Mask
import math
import os
import server

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")


class AddSubtitlesToFramesNodeX:
    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "images": ("IMAGE",),
                "alignment": ("whisper_alignment",),
                "font_color": ("STRING", {
                    "default": "white"
                }),
                "font_family": (os.listdir(FONT_DIR),),
                "font_size": ("INT", {
                    "default": 100,
                    "step": 5,
                    "display": "number"
                }),
                "fill_font_bg": ("BOOLEAN", {
                    "default": False
                }),
                "font_bg_color": ("STRING", {
                    "default": "white"
                }),
                "x_position": ("INT", {
                    "default": 100,
                    "step": 50,
                    "display": "number"
                }),
                "y_position": ("INT", {
                    "default": 100,
                    "step": 50,
                    "display": "number"
                }),
                "center_x": ("BOOLEAN", {"default": True}),
                "center_y": ("BOOLEAN", {"default": True}),
                "video_fps": ("INT", {
                    "default": 24,
                    "step": 1,
                    "display": "number"
                }),
                "start_frame": ("INT", {"default": 0, "min": 0, "max": 1000000, "step": 1})
            },
            "optional": {
                "meta_batch": ("VHS_BatchManager",)
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE", "subtitle_coord",)
    RETURN_NAMES = ("IMAGE", "MASK", "cropped_subtitles", "subtitle_coord",)
    FUNCTION = "add_subtitles_to_frames"
    CATEGORY = "whisper"

    def add_subtitles_to_frames(self, images, alignment, font_family, font_size, font_color, x_position, y_position,
                                center_x, center_y, video_fps, fill_font_bg, font_bg_color, start_frame, meta_batch):
        if meta_batch is not None:
            prompt_queue = server.PromptServer.instance.prompt_queue
            currently_running = prompt_queue.currently_running
            (_, _, prompt, _, _) = next(iter(currently_running.values()))
            for uid in prompt:
                if prompt[uid]['class_type'] == 'VHS_BatchManager':
                    requeue = prompt[uid]['inputs'].get('requeue', 0)
                    start_frame = start_frame + requeue * meta_batch.frames_per_batch
                    print(f"Requeue: {requeue} frames_per_batch:{meta_batch.frames_per_batch} start_frame:{start_frame}")
        print(f"start_frame:{start_frame}")

        pil_images = tensor2pil(images)
        pil_images_with_text = []
        font = ImageFont.truetype(os.path.join(FONT_DIR, font_family), font_size)

        if len(alignment) == 0:
            pil_images_with_text = pil_images
        else:
            frame_dict = {}
            for i in range(len(alignment)):
                alignment_obj = alignment[i]
                start_frame_no = math.floor(alignment_obj["start"] * video_fps)
                end_frame_no = math.floor(alignment_obj["end"] * video_fps)
                for j in range(start_frame_no, end_frame_no):
                    frame_dict[j] = alignment_obj

            # delay frames 0.5 seconds to avoid overlap with previous subtitle
            delay_frames = math.floor(0.5 * video_fps)
            for i in range(len(pil_images)):
                j = i + start_frame
                alignment_obj = None
                if j in frame_dict:
                    alignment_obj = frame_dict[j]
                else:
                    for k in range(j - delay_frames, j):
                        if k in frame_dict:
                            alignment_obj = frame_dict[k]
                            break

                if alignment_obj is not None:
                    img = pil_images[i].convert("RGB")
                    width, height = img.size
                    d = ImageDraw.Draw(img)
                    # center text
                    text_bbox = d.textbbox((x_position, y_position), alignment_obj["value"], font=font)
                    if center_x:
                        text_width = text_bbox[2] - text_bbox[0]
                        x_position = (width - text_width) / 2
                    if center_y:
                        text_height = text_bbox[3] - text_bbox[1]
                        y_position = (height - text_height) / 2

                    # add text to video frames
                    if fill_font_bg:
                        d.rectangle(text_bbox, fill=font_bg_color)
                    d.text((x_position, y_position), alignment_obj["value"], fill=font_color, font=font)
                else:
                    img = pil_images[i].convert("RGB")
                pil_images_with_text.append(img)

        tensor_images = pil2tensor(pil_images_with_text)

        return (tensor_images,)
