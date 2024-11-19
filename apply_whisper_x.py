import whisper
import os
import folder_paths
import uuid
import torchaudio
import translators as ts


class ApplyWhisperNodeX:
    @classmethod
    def INPUT_TYPES(s):
        translator_list = ['alibaba', 'apertium', 'argos', 'baidu', 'bing',
                           'caiyun', 'cloudTranslation', 'deepl', 'elia', 'google',
                           'hujiang', 'iciba', 'iflytek', 'iflyrec', 'itranslate',
                           'judic', 'languageWire', 'lingvanex', 'mglip', 'mirai',
                           'modernMt', 'myMemory', 'niutrans', 'papago', 'qqFanyi',
                           'qqTranSmart', 'reverso', 'sogou', 'sysTran', 'tilde',
                           'translateCom', 'translateMe', 'utibet', 'volcEngine', 'yandex',
                           'yeekit', 'youdao']
        lang_list = ["zh", "en", "ja", "ko", "ru", "fr", "de", "es", "pt", "it", "ar"]
        return {
            "required": {
                "audio": ("AUDIO",),
                "model": (["base", "tiny", "small", "medium", "large"],),
                "if_translate": ("BOOLEAN", {
                    "default": False
                }),
                "translator": (translator_list, {
                    "default": "alibaba"
                }),
                "to_language": (lang_list, {
                    "default": "en"
                })
            }
        }

    RETURN_TYPES = ("STRING", "whisper_alignment", "whisper_alignment", "whisper_alignment")
    RETURN_NAMES = ("text", "segments_alignment", "words_alignment", "translate_alignment")
    FUNCTION = "apply_whisper"
    CATEGORY = "whisper"

    def apply_whisper(self, audio, model, if_translate, translator, to_language):

        # save audio bytes from VHS to file
        temp_dir = folder_paths.get_temp_directory()
        os.makedirs(temp_dir, exist_ok=True)
        audio_save_path = os.path.join(temp_dir, f"{uuid.uuid1()}.wav")
        torchaudio.save(audio_save_path, audio['waveform'].squeeze(
            0), audio["sample_rate"])

        # transribe using whisper
        model = whisper.load_model(model)
        result = model.transcribe(audio_save_path, word_timestamps=True)

        segments = result['segments']
        segments_alignment = []
        words_alignment = []
        translate_alignments = []

        for segment in segments:
            # create segment alignments
            segment_dict = {
                'value': segment['text'].strip(),
                'start': segment['start'],
                'end': segment['end']
            }
            segments_alignment.append(segment_dict)
            if if_translate:
                # unicode to utf-8
                translator_dict = {
                    'value': ts.translate_text(query_text=segment['text'].strip(), translator=translator, to_language=to_language).encode('utf-8'),
                    'start': segment['start'],
                    'end': segment['end']
                }
                translate_alignments.append(translator_dict)

            # create word alignments
            for word in segment["words"]:
                word_dict = {
                    'value': word["word"].strip(),
                    'start': word["start"],
                    'end': word['end']
                }
                words_alignment.append(word_dict)

        if if_translate:
            return (result["text"].strip(), segments_alignment, words_alignment, translate_alignments)
        else:
            return (result["text"].strip(), segments_alignment, words_alignment, segments_alignment)
