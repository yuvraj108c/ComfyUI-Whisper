import whisper
import os
import folder_paths
import uuid
import torchaudio

WHISPER_MODEL_SUBDIR = os.path.join("stt", "whisper")


class ApplyWhisperNode:
    languages_by_name = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "model": (['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large', 'large-v3-turbo', 'turbo'],),
            },
            "optional": {
                "language": (
                    ["auto"] +
                    [s.capitalize() for s in sorted(list(whisper.tokenizer.LANGUAGES.values())) ],
                ),
            }
        }

    RETURN_TYPES = ("STRING", "whisper_alignment", "whisper_alignment")
    RETURN_NAMES = ("text", "segments_alignment", "words_alignment")
    FUNCTION = "apply_whisper"
    CATEGORY = "whisper"

    def apply_whisper(self, audio, model, language):

        # save audio bytes from VHS to file
        temp_dir = folder_paths.get_temp_directory()
        os.makedirs(temp_dir, exist_ok=True)
        audio_save_path = os.path.join(temp_dir, f"{uuid.uuid1()}.wav")
        torchaudio.save(audio_save_path, audio['waveform'].squeeze(
            0), audio["sample_rate"])

        # transribe using whisper
        model = whisper.load_model(model, download_root=os.path.join(folder_paths.models_dir, WHISPER_MODEL_SUBDIR))
        transcribe_args = {}
        if language != "auto":
            if ApplyWhisperNode.languages_by_name is None:
                ApplyWhisperNode.languages_by_name = {v.lower(): k for k, v in whisper.tokenizer.LANGUAGES.items()}
            transcribe_args['language'] = ApplyWhisperNode.languages_by_name[language.lower()]
        result = model.transcribe(audio_save_path, word_timestamps=True, **transcribe_args)

        segments = result['segments']
        segments_alignment = []
        words_alignment = []

        for segment in segments:
            # create segment alignments
            segment_dict = {
                'value': segment['text'].strip(),
                'start': segment['start'],
                'end': segment['end']
            }
            segments_alignment.append(segment_dict)

            # create word alignments
            for word in segment["words"]:
                word_dict = {
                    'value': word["word"].strip(),
                    'start': word["start"],
                    'end': word['end']
                }
                words_alignment.append(word_dict)

        return (result["text"].strip(), segments_alignment, words_alignment)
