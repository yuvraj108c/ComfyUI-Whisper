import whisper
import os
import folder_paths
import uuid
import torchaudio
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import tempfile
import time
import re

class ApplyWhisperNode:
    languages_by_name = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "model": (["base", "tiny", "small", "medium", "large"],),
            },
            "optional": {
                "language": (
                    ["auto"] +
                    [s.capitalize() for s in sorted(list(whisper.tokenizer.LANGUAGES.values())) ],
                ),
                "min_silence_len": ("INT", {"default": 300, "min": 50, "max": 1000, "step": 50}),
                "silence_thresh": ("INT", {"default": -40, "min": -60, "max": -20, "step": 5}),
            }
        }

    RETURN_TYPES = ("STRING", "whisper_alignment", "whisper_alignment")
    RETURN_NAMES = ("text", "segments_alignment", "words_alignment")
    FUNCTION = "apply_whisper"
    CATEGORY = "whisper"

    def remove_punctuation(self, text):
        """移除所有标点符号，但保留小数点和百分号，并用空格替换其他符号"""
        # 使用正则表达式移除非保留字符
        text = re.sub(r'[^\w\s.%]', ' ', text)
        # 将多个连续空格替换为单个空格
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def apply_whisper(self, audio, model, language="auto", min_silence_len=300, silence_thresh=-40):
        # save audio bytes from VHS to file
        temp_dir = folder_paths.get_temp_directory()
        os.makedirs(temp_dir, exist_ok=True)
        audio_save_path = os.path.join(temp_dir, f"{uuid.uuid1()}.wav")
        torchaudio.save(audio_save_path, audio['waveform'].squeeze(0), audio["sample_rate"])

        # Load audio with pydub for silence detection
        audio_segment = AudioSegment.from_wav(audio_save_path)
        
        # Detect non-silent segments
        non_silent_segments = detect_nonsilent(
            audio_segment,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh,
            seek_step=10
        )
        
        # Load whisper model
        model = whisper.load_model(model)
        transcribe_args = {}
        if language != "auto":
            if ApplyWhisperNode.languages_by_name is None:
                ApplyWhisperNode.languages_by_name = {v.lower(): k for k, v in whisper.tokenizer.LANGUAGES.items()}
            transcribe_args['language'] = ApplyWhisperNode.languages_by_name[language.lower()]
        
        segments_alignment = []
        words_alignment = []
        full_text = ""
        
        # Process each non-silent segment
        for i, (start_ms, end_ms) in enumerate(non_silent_segments):
            # Convert to seconds
            start_time = start_ms / 1000.0
            end_time = end_ms / 1000.0
            
            # Extract segment audio
            segment_audio = audio_segment[start_ms:end_ms]
            
            # Create a temporary file path
            temp_audio_path = os.path.join(temp_dir, f"temp_segment_{uuid.uuid4()}.wav")
            
            # Export segment to file
            segment_audio.export(temp_audio_path, format="wav")
            
            try:
                # Transcribe segment
                result = model.transcribe(temp_audio_path, word_timestamps=True, **transcribe_args)
                
                # Add segment to alignment list
                if result['segments']:
                    segment = result['segments'][0]
                    # 移除标点符号并用空格替换
                    segment_text = self.remove_punctuation(segment['text'])
                    segment_dict = {
                        'value': segment_text,
                        'start': segment['start'] + start_time,  # Adjust time to absolute position
                        'end': segment['end'] + start_time
                    }
                    segments_alignment.append(segment_dict)
                    full_text += segment_text + " "
                    
                    # Add words to alignment list
                    for word in segment.get("words", []):
                        # 移除标点符号并用空格替换
                        word_text = self.remove_punctuation(word["word"])
                        word_dict = {
                            'value': word_text,
                            'start': word["start"] + start_time,  # Adjust time to absolute position
                            'end': word['end'] + start_time
                        }
                        words_alignment.append(word_dict)
            except Exception as e:
                print(f"Error transcribing segment {i}: {e}")
            finally:
                # Try to delete the temporary file with retries
                self._safe_delete_file(temp_audio_path)
        
        # If no segments were found, fall back to original method
        if not segments_alignment:
            result = model.transcribe(audio_save_path, word_timestamps=True, **transcribe_args)
            segments = result['segments']
            
            for segment in segments:
                # 移除标点符号并用空格替换
                segment_text = self.remove_punctuation(segment['text'])
                # create segment alignments
                segment_dict = {
                    'value': segment_text,
                    'start': segment['start'],
                    'end': segment['end']
                }
                segments_alignment.append(segment_dict)
                full_text += segment_text + " "

                # create word alignments
                for word in segment["words"]:
                    # 移除标点符号并用空格替换
                    word_text = self.remove_punctuation(word["word"])
                    word_dict = {
                        'value': word_text,
                        'start': word["start"],
                        'end': word['end']
                    }
                    words_alignment.append(word_dict)
        
        # Clean up audio file
        self._safe_delete_file(audio_save_path)
            
        return (full_text.strip(), segments_alignment, words_alignment)
    
    def _safe_delete_file(self, file_path, max_retries=5, delay=0.1):
        """Safely delete a file with retries to handle file locking issues"""
        for i in range(max_retries):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
            except (PermissionError, OSError) as e:
                if i < max_retries - 1:
                    time.sleep(delay)
                else:
                    print(f"Warning: Could not delete file {file_path}: {e}")
                    return False
        return False