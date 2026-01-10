from PIL import ImageDraw, ImageFont, Image
from .utils import tensor2pil, pil2tensor, tensor2Mask
import math
import os
import textwrap

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
                    "default": 100,
                    "step":5,
                    "display": "number"
                }),
                "x_position": ("INT",{
                    "default": 100,
                    "step":50,
                    "display": "number"
                }),
                "y_position": ("INT",{
                    "default": 100,
                    "step":50,
                    "display": "number"
                }),
                "center_x": ("BOOLEAN", {"default": True}),
                "center_y": ("BOOLEAN", {"default": True}),
                "video_fps": ("FLOAT",{
                    "default": 24.0,
                    "step":1,
                    "display": "number"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE", "subtitle_coord", )
    RETURN_NAMES = ("IMAGE","MASK", "cropped_subtitles","subtitle_coord",)
    FUNCTION = "add_subtitles_to_frames"
    CATEGORY = "whisper"

    def wrap_text(self, text, font, max_width):
        """将文本分成多行，确保每行宽度不超过max_width"""
        # 如果文本宽度已经小于最大宽度，直接返回单行
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            return [text]
        
        # 使用textwrap进行分行
        wrapper = textwrap.TextWrapper(width=int(len(text) * max_width / text_width))
        wrapped_lines = wrapper.wrap(text)
        
        # 进一步检查每行宽度，确保不超过最大宽度
        final_lines = []
        for line in wrapped_lines:
            line_bbox = font.getbbox(line)
            line_width = line_bbox[2] - line_bbox[0]
            
            if line_width <= max_width:
                final_lines.append(line)
            else:
                # 如果仍然太宽，逐字符分割
                current_line = ""
                for char in line:
                    test_line = current_line + char
                    test_bbox = font.getbbox(test_line)
                    test_width = test_bbox[2] - test_bbox[0]
                    
                    if test_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            final_lines.append(current_line)
                        current_line = char
                
                if current_line:
                    final_lines.append(current_line)
        
        return final_lines

    def add_subtitles_to_frames(self, images, alignment, font_family, font_size, font_color, x_position, y_position, center_x, center_y, video_fps):
        pil_images = tensor2pil(images)

        pil_images_with_text = []
        cropped_pil_images_with_text = []
        pil_images_masks = []
        subtitle_coord = []

        font = ImageFont.truetype(os.path.join(FONT_DIR,font_family), font_size)

        if len(alignment) == 0:
            pil_images_with_text = pil_images
            cropped_pil_images_with_text = pil_images
            subtitle_coord.extend([(0,0,0,0)]*len(pil_images))

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

                # create mask + cropped image
                black_img = Image.new('RGB', (width, height), 'black')
                pil_images_masks.append(black_img)
                black_img = Image.new('RGB', (1, 1), 'black') # to prevent max() from considering these images, use very small size
                cropped_pil_images_with_text.append(black_img)  
                subtitle_coord.append((0,0,0,0))


            for i in range(start_frame_no,end_frame_no):
                img = pil_images[i].convert("RGB")
                width, height = img.size

                d = ImageDraw.Draw(img)

                # 计算最大允许宽度（视频宽度减去左右各50像素）
                max_text_width = width - 100
                
                # 分行文本
                text_lines = self.wrap_text(alignment_obj["value"], font, max_text_width)
                
                # 计算文本总高度
                total_text_height = 0
                line_heights = []
                for line in text_lines:
                    line_bbox = font.getbbox(line)
                    line_height = line_bbox[3] - line_bbox[1]
                    line_heights.append(line_height)
                    total_text_height += line_height
                
                # 添加行间距（假设为字体大小的20%）
                line_spacing = int(font_size * 0.2)
                total_text_height += line_spacing * (len(text_lines) - 1)
                
                # 计算起始Y位置
                if center_y:
                    current_y = (height - total_text_height) / 2
                else:
                    current_y = y_position
                
                # 绘制每一行文本
                text_bboxes = []  # 存储每行文本的边界框
                for line in text_lines:
                    line_bbox = font.getbbox(line)
                    line_width = line_bbox[2] - line_bbox[0]
                    
                    # 计算X位置
                    if center_x:
                        line_x = (width - line_width) / 2
                    else:
                        line_x = x_position
                    
                    # 绘制文本到视频帧
                    d.text((line_x, current_y), line, fill=font_color, font=font)
                    
                    # 记录文本位置和大小
                    text_bbox = (line_x, current_y, line_x + line_width, current_y + line_heights[text_lines.index(line)])
                    text_bboxes.append(text_bbox)
                    
                    # 更新Y位置
                    current_y += line_heights[text_lines.index(line)] + line_spacing
                
                # 计算整个文本区域的最小边界框
                if text_bboxes:
                    min_x = min(bbox[0] for bbox in text_bboxes)
                    min_y = min(bbox[1] for bbox in text_bboxes)
                    max_x = max(bbox[2] for bbox in text_bboxes)
                    max_y = max(bbox[3] for bbox in text_bboxes)
                    overall_bbox = (min_x, min_y, max_x, max_y)
                else:
                    overall_bbox = (0, 0, 0, 0)
                
                pil_images_with_text.append(img)

                # 创建mask
                black_img = Image.new('RGB', (width, height), 'black')
                d_mask = ImageDraw.Draw(black_img)
                
                # 在mask上绘制文本
                current_y_mask = current_y = (height - total_text_height) / 2 if center_y else y_position
                for line in text_lines:
                    line_bbox = font.getbbox(line)
                    line_width = line_bbox[2] - line_bbox[0]
                    
                    if center_x:
                        line_x = (width - line_width) / 2
                    else:
                        line_x = x_position
                    
                    d_mask.text((line_x, current_y_mask), line, fill="white", font=font)
                    current_y_mask += line_heights[text_lines.index(line)] + line_spacing
                
                pil_images_masks.append(black_img)    

                # 裁剪字幕区域
                if text_bboxes:
                    cropped_text_frame = black_img.crop(overall_bbox)
                else:
                    cropped_text_frame = Image.new('RGB', (1, 1), 'black')
                
                cropped_pil_images_with_text.append(cropped_text_frame)
                subtitle_coord.append(overall_bbox)

            
            last_frame_no = end_frame_no

        # add missing frames with no text at end
        for i in range(len(pil_images_with_text),len(pil_images)):
            pil_images_with_text.append(pil_images[i])
            width,height = pil_images[i].size

            # create mask + cropped image
            black_img = Image.new('RGB', (width, height), 'black')
            pil_images_masks.append(black_img)
            black_img = Image.new('RGB', (1, 1), 'black') # to prevent max() from considering these images, use very small size
            cropped_pil_images_with_text.append(black_img)  
            subtitle_coord.append((0,0,0,0))

        # make cropped images same size
        cropped_pil_images_with_text_normalised = []
        max_width = max(img.width for img in cropped_pil_images_with_text)
        max_height = max(img.height for img in cropped_pil_images_with_text)

        for img in cropped_pil_images_with_text:
            blank_frame = Image.new("RGB", (max_width, max_height), "black")
            blank_frame.paste(img, (0,0))
            cropped_pil_images_with_text_normalised.append(blank_frame)


        tensor_images = pil2tensor(pil_images_with_text)
        cropped_pil_images_with_text_normalised = pil2tensor(cropped_pil_images_with_text_normalised)
        tensor_masks = tensor2Mask(pil2tensor(pil_images_masks))

        return (tensor_images,tensor_masks,cropped_pil_images_with_text_normalised,subtitle_coord,)