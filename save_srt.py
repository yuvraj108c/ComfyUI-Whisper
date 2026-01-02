# mostly generated using claude

import folder_paths
import json
import os

class SaveSRTNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "alignment" : ("whisper_alignment",),
                "name": ("STRING",{"default": "subtitles"}),
            }
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("srt_path",)
    FUNCTION = "save_srt"
    CATEGORY = "whisper"

    def seconds_to_srt_time(self, seconds):
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

    def json_to_srt(self, json_data):
        """Convert JSON subtitle data to SRT format"""
        
        # Parse JSON if it's a string
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        # Generate SRT content
        srt_content = []
        for i, entry in enumerate(data, start=1):
            start_time = self.seconds_to_srt_time(entry['start'])
            end_time = self.seconds_to_srt_time(entry['end'])
            text = entry['value']
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(text)
            srt_content.append("")  # Empty line between entries

        return srt_content

    def save_srt(self, alignment, name):

        subfolder = "srt"
        output_dir = os.path.join(folder_paths.get_output_directory(), subfolder)
        os.makedirs(output_dir,exist_ok=True)

        srt_save_path = os.path.join(output_dir, name) + ".srt"
        srt_content = self.json_to_srt(alignment)

        with open(srt_save_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))

        return (srt_save_path,)
